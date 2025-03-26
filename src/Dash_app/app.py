"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location, and a callback uses the
current location to render the appropriate page content. The active prop of
each NavLink is set automatically according to the current pathname. To use
this feature you must install dash-bootstrap-components >= 0.11.0.
s
For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""

from pathlib import Path
import os
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State

from src.dashboard.components.sidebar import create_sidebar
# from pages.resource_monitor import create_page

img_src = Path("src", "dashboard", "components", "assets")
asst_path = os.path.join(os.getcwd(), "assets")


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], 
                use_pages=True,
                assets_folder="assets",
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                )


# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


sidebar = create_sidebar()

content = html.Div(id="page-content", style=CONTENT_STYLE)

# app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

app.layout = html.Div([
    sidebar, 
    dash.page_container
], style=CONTENT_STYLE)


# @app.callback(
#     Output("sidebar", "className"),
#     [Input("sidebar-toggle", "n_clicks")],
#     [State("sidebar", "className")],
# )
# def toggle_classname(n, classname):
#     if n and classname == "":
#         return "collapsed"
#     return ""


# @app.callback(
#     Output("collapse", "is_open"),
#     [Input("navbar-toggle", "n_clicks")],
#     [State("collapse", "is_open")],
# )
# def toggle_collapse(n, is_open):
#     if n:
#         return not is_open
#     return is_open


if __name__ == "__main__":
    app.run(port=8888, debug=True)
