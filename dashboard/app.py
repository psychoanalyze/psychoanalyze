from dash import Dash, html
import dash
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink("Simulate", href="/simulate")),
                dbc.NavItem(dbc.NavLink("JNE Paper", href="/paper")),
                dbc.NavItem(dbc.NavLink("Upload", href="/upload")),
            ],
            brand="PsychoAnalyze",
            brand_href="/",
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
