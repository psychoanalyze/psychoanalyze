import dash_bootstrap_components as dbc

simulate = dbc.NavbarSimple(
    [
        dbc.NavItem(
            dbc.NavLink("Bayes", href="/simulate/bayes"),
        ),
        dbc.NavItem(dbc.NavLink("ECDFs", href="/simulate/ecdfs")),
        dbc.NavItem(dbc.NavLink("Strength-Duration", href="/simulate/sd")),
        dbc.NavItem(dbc.NavLink("Thresholds", href="/simulate/thresholds")),
        dbc.NavItem(dbc.NavLink("Block", href="/simulate/block")),
    ],
)
