# Import packages
from dash import Dash, html, dash_table, dcc, Input, Output, State

## For darkmode, NOT used here
import dash_bootstrap_components as dbc
import dash_bootstrap_templates
from dash_bootstrap_templates import load_figure_template

## For plots
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

##For real-time data from mac
import psutil
import datetime

## For toggle swith
import dash_daq as daq


# load_figure_template(["cyborg", "darkly"]) --> if we wwant to use dark mode

# Used data
df = pd.read_csv('my_code_NOT_pushed/cpu_gpu_usage.csv')

# Initialize the app
app = Dash()

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

####### Retrieve battery life info ON MAC ONLY
def get_battery_info():
    battery = psutil.sensors_battery()

    if battery is not None:
        print("Battery Percentage:", battery.percent, "%")
        print("Power plugged in:", battery.power_plugged)

        def convertTime(seconds):
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return "%d:%02d:%02d" % (hours, minutes, seconds)

        print("Battery remaining time:", convertTime(battery.secsleft))
    
    else:
        print("You are plugged in.")

#print(get_battery_info())

# App layout
app.layout = html.Div([
     
    html.H2(children='Marisa is trying out Dash'),
    dash_table.DataTable(data=df.to_dict('records'), page_size=5), # Just showing for me to check my columns
    
    dcc.Graph(id = 'utilization_graph', figure = create_figure()),

    daq.ToggleSwitch(
        id='show_means_switch',
        value=False,
        label='Show means',
        labelPosition='bottom'
),
####### Trying with callback for memory_usage

    html.H4('Real-time memory usage'),
    dcc.Graph(id="memory_graph"),
    dcc.Checklist(
        id = 'memory_checklist',
        options=[{"label": "CPU RAM", "value": "cpu RAM"},
                 {"label": "GPU RAM", "value": "gpu RAM"},
                 {"label": "NPU RAM", "value": "npu RAM"}],
        value=["cpu RAM"],
        inline=True
       ),

    dcc.Interval(
        id="interval-component",
        interval=1000,  # Change to update every X seconds
        n_intervals=0
    ),
    
    dcc.Store(id="memory_store", data={"timestamp": [], "cpu RAM": [], "gpu RAM": [], "npu RAM": []}) # To use in state in callback

])

## Callback for plot 1: Utilization
@app.callback(
    Output("utilization_graph", "figure"),
    Input("show_means_switch", "value")
)
def update_utilization_graph(show_means):
    return create_figure(show_means)

## Callback for plot 2: Memory
@app.callback(
    [Output("memory_graph", "figure"),
     Output("memory_store", "data")],
    [Input("memory_checklist", "value"),
     Input("interval-component", "n_intervals")],
    State("memory_store", "data")
)
def update_line_chart(selected_processor_type, n_intervals, stored_data):
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
    
    #fig.update_xaxes(
    #    dtick=5000)# have a tick only every 5 seconds --> not working as I'd like to

    
    return fig, stored_data

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
