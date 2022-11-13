from dash import Dash, html
import dash
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink("ECDF", href="/simulate-ecdfs")),
                dbc.NavItem(dbc.NavLink("Strength-Duration", href="/simulate-sd")),
                dbc.NavItem(dbc.NavLink("Thresholds", href="/simulate-thresholds")),
                dbc.NavItem(dbc.NavLink("Bayes", href="/simulate-bayesian")),
            ],
            brand="PsychoAnalyze",
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
