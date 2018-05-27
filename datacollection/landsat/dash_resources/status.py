import dash_core_components as dcc
import dash_html_components as html

import datacollection.landsat.dash_resources.html_elem as html_elem


#################### PAUSING ####################
pausing_div = html.Div([
    html.Label('Service Status', style=html_elem.CONTENT_TITLE_STYLE),
    html.Hr(style={'margin-top': 10, 'margin-bottom': 15}),
    html.Div([html.Button(
        'Shutdown', id='shutdown',
        style={'width': 600, 'color': '#e50f04'}
    )]),
    html.Div([html.Button(
        'Pause Master', id='pause-master',
        style={'width': 600, 'color': '#2ffc14'}
    )], style={'margin-top': 10}),
    html.Div([
        html.Button(
            'Pause Preprocessing', id='pause-preproc',
            style={'width': 295, 'color': '#2ffc14'}
        ),
        html.Button(
            'Pause Downloading', id='pause-download',
            style={'margin-left': 10, 'width': 295, 'color': '#2ffc14'}
        )
    ], style={'margin-top': 10})
], style={'margin-bottom': 20})


stats_div = html.Div([
    html.Label('Service Statistics', style=html_elem.CONTENT_TITLE_STYLE),
    html.Hr(style={'margin-top': 10, 'margin-bottom': 15}),
])


layout = [
    pausing_div,
    stats_div
]
