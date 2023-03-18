from dash import html
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardLink(html.H4("Simulate"), href="/simulate"),
                            html.P("Simulate data from a Yes/No task."),
                        ],
                        body=True,
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardLink(html.H4("Experiments"), href="/paper/summary"),
                            html.P(
                                "View interactive versions of the figures"
                                + " from Schlichenmeyer et al., 2022."
                            ),
                        ],
                        body=True,
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardLink(html.H4("Upload"), href="/upload"),
                            html.P(
                                "Upload your own data set and try our "
                                + "interactive data exploration tool. Your "
                                + "data never leaves the browser."
                            ),
                        ],
                        body=True,
                    )
                ),
            ]
        ),
    ]
)
