from dash import Dash, html
import dash
import dash_bootstrap_components as dbc


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.SUPERHERO, dbc.icons.BOOTSTRAP],
    use_pages=True,
)
server = app.server

app.layout = html.Div(
    [
        dbc.NavbarSimple(
            [
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            "GitHub",
                            href="https://github.com/psychoanalyze/psychoanalyze",
                        ),
                        html.I(className="bi bi-github"),
                    ],
                    className="d-flex align-items-center mx-2",
                ),
                dbc.NavItem(
                    [
                        dbc.NavLink(
                            "Documentation",
                            href="https://psychoanalyze.github.io",
                        ),
                        html.I(className="bi bi-book"),
                    ],
                    className="d-flex align-items-center mx-2",
                ),
            ],
            brand=dbc.Col(
                [
                    dbc.Row(html.H1("PsychoAnalyze")),
                    dbc.Row(html.P("Interactive data exploration for psychophysics.")),
                ],
            ),
            brand_href="/",
        ),
        dash.page_container,
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
