import dash
# from src.dashboard.components.chatbot_button import get_popover_chatbot

# Import packages
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

#dash.register_page(__name__, path='/')

title_section = html.Div([
    html.Br(),

    # HP logo
    html.Img(src='/assets/0_HP_logo.png', style={'width': '80px', 
                                                 'height': 'auto', 
                                                 'margin-right': '20px'}),  
    # Title and subtitle
    html.Div([
        html.H1('AI Performance Showcase: CPU, GPU, and NPU on HP Mobile Workstations',
                style={'color': '#004ad8', 'margin': '5px', 'font-weight': 'bold'}),
        html.H3("Experience how NPUs are shaping the future of mobile AI",
                style={'margin-top': '5px'}) 
    ]),

    # Styling the flex box
    ], style={'display': 'flex', ## keep otherwise will stack logo on text
          'align-items': 'center', 
          'justify-content': 'flex-start', 
          'margin-bottom': '20px',
          'padding-left': '20px',
          'padding-top': '50px' })

#### Alternative layout
'''
content = html.Div([
    # HP Logo
    html.Div([
        html.Img(src='/assets/0_HP_logo.png', style={'width': '120px', 'display': 'block', 'margin': '20px auto'})
    ]),

    # Title
    html.H1('AI Performance Showcase: CPU, GPU, and NPU on HP Mobile Workstations'),
    
    #Subtitle
    html.H2("Experience how NPUs are shaping the future of mobile AI"),
'''
# Image section

images_section = html.Div([
        # Image 1
        html.Div([
            html.Img(src='/assets/1_HP_ZBook_Power.png', style={'width': '500px','height': 'auto', 'margin': '20px'}),
            html.H4('ZBook Power'),
            html.Br(),
            html.P('Intel Core U9, RTX 3000 Ada (8GB)', style={'margin-top': '5px'}),
        ], style={'display': 'inline-block', 'text-align': 'center'}),
        
        # Image 2
        html.Div([
            html.Img(src='/assets/2_HP_Firefly.png', style={'width': '500px','height': 'auto', 'margin': '20px'}),
            html.H4('ZBook Firefly'),
            html.Br(),
            html.P('Intel Core U7 (NPU) with RTX A500', style={'margin-top': '5px'}),
        ], style={'display': 'inline-block', 'text-align': 'center'}),
        
        # Image 3
        html.Div([
            html.Img(src='/assets/3_HP_ZBook_Ultra.png', style={'width': '520px','height': 'auto', 'margin': '20px'}),
            html.H4('ZBook Ultra'),
            html.Br(),
            html.P('AMD SOC, 128GB RAM with up to 96GB VRAM', style={'margin-top': '5px'}),
        ], style={'display': 'inline-block', 'text-align': 'center'})
    ], style={'text-align': 'center', 'margin-top': '20px'})

# App description section
description_box = html.Div([
    dcc.Markdown("""
                **Welcome to the AI Performance Showcase**
                 
                This app explores processor capabilities for mobile AI on HP mobile workstations. 
                 
                **Explore & Experiment**
                 
                - Upload a PDF and perform question-answering on its content
                - Try out an image classification task
                - Click the chatbot button to get information about HP workstations
                 
                """)
    ],
        style={
            'background-color': '#e5e5e5', 
            'color': '#004ad8',
            'border-radius': '10px',  # Rounded corners
            'padding': '20px',  # Padding around the content
            'margin-top': '20px',  # Top margin to separate from images
            'max-width': '800px',  # Max width to keep the box compact
            'margin-left': 'auto',
            'margin-right': 'auto'
    })

# Footer image
footer_image = html.Div([
    html.Img(src='/assets/4_footer.png', style={'width': '100%', 'height': '40px','margin-top': '30px'})
])

app.layout = html.Div([
    title_section,
    images_section,
    description_box,
    footer_image,
    #get_popover_chatbot()
])

# Run the app
if __name__ == '__main__':
    app.run(debug=True)