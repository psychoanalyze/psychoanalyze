from dash import Dash, html
import dash
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB], use_pages=True)

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(dbc.NavLink("Simulate", href="/simulate")),
                # dbc.DropdownMenu(
                #     [
                #         dbc.DropdownMenuItem("ECDF", href="/simulate/ecdfs"),
                #         dbc.DropdownMenuItem("Strength-Duration", href="sd"),
                #         dbc.DropdownMenuItem("Thresholds", href="thresholds"),
                #         dbc.DropdownMenuItem("Bayes", href="bayes"),
                #     ],
                #     label="Simulate",
                #     nav=True,
                #     in_navbar=True,
                # ),
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem("Summary", href="/paper/summary"),
                    ],
                    label="JNE Data",
                    nav=True,
                    in_navbar=True,
                ),
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
