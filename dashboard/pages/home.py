from dash import html
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")

layout = dbc.Container(
    [
        html.H1("Welcome to PsychoAnalyze!"),
        html.P("Analyze psychophysics data with ease."),
        html.P("Get started by choosing an option below"),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardLink(html.H4("Simulate"), href="/simulate/ecdfs"),
                            html.P("Simulate psychophysics data"),
                        ],
                        body=True,
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardLink(html.H4("JNE Data"), href="/paper/summary"),
                            html.P("View the dataset from Schlichenmeyer et al., 2022"),
                        ],
                        body=True,
                    )
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardLink(html.H4("Upload"), href="/"),
                            html.P("Upload your own data set"),
                        ],
                        body=True,
                    )
                ),
            ]
        ),
    ]
)
