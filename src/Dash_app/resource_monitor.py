from pathlib import Path

import dash
app = dash.get_app()

from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import platform
import psutil
#import GPUtil
import numpy as np
import dash_daq as daq


## For plots
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

##For real-time data from mac
import psutil
import datetime

dash.register_page(__name__)

#deviceIDs = GPUtil.getAvailable(order = 'first', limit = 1, maxLoad = 0.5, maxMemory = 0.5, includeNan=False, excludeID=[], excludeUUID=[])


##### STATIC PLOT: USAGE OVER TIME
#df = pd.read_csv(Path("..", "..", "data", "test", 'cpu_gpu_usage.csv'))
df = pd.read_csv('./cpu_gpu_usage.csv') # just for testing

df["timestamp"] = pd.to_datetime(df["timestamp"])
x_max = df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]
x_time = np.arange(x_max.total_seconds() + 1) 
df["seconds"] = x_time


## Static plot
def create_figure(show_means=False):
    fig = px.line(df, x='timestamp', y=['cpu_usage', 'gpu_usage'], 
                title='CPU & GPU utilization over time', 
                labels={'value': 'Usage (%)', 'timestamp': 'Time'},
                markers=False)
    
    # Adding the mean lines if that's something we want to use. 
    if show_means:
            cpu__usage_mean = df['cpu_usage'].mean()
            gpu__usage_mean = df['gpu_usage'].mean()

            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=[cpu__usage_mean] * len(df),
                mode='lines', line=dict(color='blue', dash='dash'),
                name='CPU usage mean'
            ))

            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=[gpu__usage_mean] * len(df),
                mode='lines', line=dict(color='red', dash='dash'),
                name='GPU usage mean'
            ))

    return fig

##### Static plot comparing execution times on 3 types:
fake_execution_time = {
    "Image_classification": {
        "cpu": 45.2,  
        "gpu": 15.8, 
        "npu": 12.4 
    },
    "LLM_QA": {
        "cpu": 120.5,  
        "gpu": 45.3,   
        "npu": 35.1  
    }}
fake_execution_time_df = pd.DataFrame.from_dict(fake_execution_time)
#print(fake_execution_time_df)

df_fake_execution_time_melted = fake_execution_time_df.reset_index().melt(id_vars=["index"], var_name="Task", value_name="Execution_time")
df_fake_execution_time_melted.rename(columns={"index": "Processor"}, inplace=True)
#print(df_fake_execution_time_melted)

fig_exec_time = px.histogram(df_fake_execution_time_melted, 
             x="Task", y="Execution_time", 
             color="Processor",
             title="Execution time comparison by processor and task",
             labels={"Execution_time": "Execution zime in seconds", "Task": "Task", "Processor": "Processor Type"},
             barmode='group')

##### Fake battery consumption data
fake_battery_consumption = {
    "Image_classification": {
        "cpu": 10.2,  
        "gpu": 5.8, 
        "npu": 4.1 
    },
    "LLM_QA": {
        "cpu": 25.5,  
        "gpu": 12.3,   
        "npu": 8.7  
    }}

fake_battery_consumption_df = pd.DataFrame.from_dict(fake_battery_consumption)
#print(fake_execution_time_df)

fake_battery_consumption_melted = fake_battery_consumption_df.reset_index().melt(id_vars=["index"], var_name="Task", value_name="Battery_consumption")
fake_battery_consumption_melted.rename(columns={"index": "Processor"}, inplace=True)
#print(fake_battery_consumption_melted)

fig_battery = px.histogram(fake_battery_consumption_melted, 
             x="Task", y="Battery_consumption", 
             color="Processor",
             title="Battery consumption comparison by processor and task",
             labels={"Battery_consumption": "Power draw (%)", "Task": "Task", "Processor": "Processor Type"},
             barmode='group')

##### INFO CARD
cpu = platform.processor()
cpu_cores = psutil.cpu_count(logical=False)

info_card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.CardBody(
                    html.Div([
                    html.I(className="bi bi-info-circle card-title "),
                    html.P(" General Info", className="card-title fw-semibold"),
                    ],
                    className="fs-4 align-middle d-flex gap-4"
                    ),
                    class_name="pb-0 ml-20"
                )
            ],
            class_name="g-0 p-0 mb-0 align-items-center"
        ),
        dbc.Row([
            dbc.Col(html.P(""), className="col-md-2 p-0"),
                dbc.Col(
                        html.P([f"CPU: {cpu} ({cpu_cores} Cores) ", html.Br(),
                                   "LLM picked ", html.Br(),
                                   "Task picked"],
                                   className="mt-0 text-muted"),
                    class_name="col-md-8 d-flex"
                )
            ],
            class_name="g-0 mb-0 mt-0",
        )
    ],
    style={"width": "24rem"}
)

cpu_util = html.Div(
    [
        html.H5("Processor Utilisation"),
        dcc.Graph(id='cpu-usage')
    ]
)

gpu_util = html.Div(
    [
        html.H5("GPU Utilisation"),
        dcc.Graph(id='gpu-usage'),
    ]
)

util = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(cpu_util, width="auto", md=6),
                dbc.Col(gpu_util, width="auto", md=6)
            ],
        ),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        ),
    ],
    className="pt-4 pb-4"
)

### CALLBACKS

## Callback for plot 1: Utilization
@app.callback(

    Output("utilization_graph", "figure"),
    Input("show_means_switch", "value")
)
def update_utilization_graph(show_means):
    return create_figure(show_means)

@callback(
        Output("cpu-usage", "figure"),
        Input('interval-component', "n_intervals")
)
def graph_cpu_freq(n_intervals):
    cpu_load = [(x/psutil.cpu_count()) * 100 for x in psutil.getloadavg()][1]
    # x_used = psutil.cpu_percent()
    x_unused = 100 - cpu_load
    labels = ["CPU usage", "Unused"]
    fig = go.Figure(data=[go.Pie(labels=labels, values=[cpu_load, x_unused], hole=.3)],
                    layout=go.Layout(margin={'t': 0}, height=300, width=300, showlegend=False))
    return fig

@callback(
        Output("gpu-usage", "figure"),
        Input('interval-component', "n_intervals")
)
def graph_gpu_freq(n_clicks):
    #GPUs = GPUtil.getGPUs() -->commented because I don't have that. MD
    GPUs = 'placeholder' # and added this
    if not GPUs:
        return
    #gpu = GPUs[0] -->commented because I don't have that. MD
    # gpu_load = gpu.load * 100
    gpu_load = 20
    # x_used = psutil.cpu_percent()
    x_unused = 100 - gpu_load
    labels = ["GPU usage", "Unused"]
    fig = go.Figure(data=[
        go.Pie(labels=labels, values=[gpu_load, x_unused], hole=.3)
        ],
        layout=go.Layout(
            margin={'t': 0}, 
            height=300,
            width=300,
            showlegend=False
            )
        )
    return fig

## Callback for plot 2: Memory
####### Retrieve real-time memory_usage ON MAC ONLY
def get_memory_usage():
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    real_time_memory_data = {
        "timestamp": timestamp,
        "cpu RAM": psutil.virtual_memory().percent, # --> Get RAM on Mac, TO DO: change for whatever we need to measure that on laptops
        "gpu RAM": 0,  # TO CHANGE
        "npu RAM": 0   # TO CHANGE
    }
    return real_time_memory_data

@app.callback(
    [Output("memory_graph", "figure"),
     Output("memory_store", "data")],
    [Input("memory_checklist", "value"),
     Input("interval-component", "n_intervals")],
     State("memory_store", "data")
)
def update_line_chart(selected_processor_type, n_intervals, stored_data):
    if stored_data is None:
        stored_data = {"timestamp": [], "cpu RAM": [], "gpu RAM": [], "npu RAM": []}

    if not selected_processor_type:
        return px.line(title="No data selected")
    
    ###### Trying with state:
    live_data = get_memory_usage()

    for key in stored_data.keys():
        stored_data[key].append(live_data[key])
    
    for key in stored_data.keys():
        stored_data[key] = stored_data[key][-60:] # keeping only 1 minute here
    
    df_live_to_show = pd.DataFrame(stored_data)

    df_melted = df_live_to_show.melt(id_vars=['timestamp'], 
                              value_vars = selected_processor_type, 
                              var_name = 'Memory type', 
                              value_name = 'Memory usage')

    fig = px.line(df_melted, x="timestamp", y="Memory usage", color="Memory type",
                  title="Memory usage in real-time")

    return fig, stored_data

### LAYOUT

def layout(**kwargs):
    page = html.Div([
        html.H1(children='Resource monitor'),
        html.Div([
            info_card,
            util,
            dcc.Graph(id = 'utilization_graph', figure=create_figure()),
             daq.ToggleSwitch(
                id='show_means_switch',
                value=False,
                label='Show means',
                labelPosition='bottom'
        )
        ]),
    
    ####### DYNAMIC PLOT : Live memory usage

    html.H4('Real-time memory usage'),
    dcc.Graph(id="memory_graph"),
    dcc.Checklist(
        id = 'memory_checklist',
        options=[{"label": "CPU RAM ", "value": "cpu RAM"},
                 {"label": "GPU RAM ", "value": "gpu RAM"},
                 {"label": "NPU RAM ", "value": "npu RAM"}],
        value=["cpu RAM"],
        inline=True
       ),

    dcc.Interval(
        id="interval-component",
        interval=1000,  # Change to update every X seconds
        n_intervals=0
    ),
    
    dcc.Store(id="memory_store", data={"timestamp": [], "cpu RAM": [], "gpu RAM": [], "npu RAM": []}), # To use in state in callback
    
    html.H4('Bla-bla'), # apparently needs a title to work
    dbc.Row([
            dbc.Col(dcc.Graph(id='Execution_time', figure=fig_exec_time), width=6),
            dbc.Col(dcc.Graph(id='Battery_consumption', figure=fig_battery), width=6)
        ]),

    ])
    return page