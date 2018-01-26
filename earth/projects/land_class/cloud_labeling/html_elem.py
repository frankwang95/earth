import dash_core_components as dcc
import dash_html_components as html


GLOBAL_STYLE = {
    'position': 'absolute',
    'width': '100%',
    'height': '100%',
    'top': 0,
    'left': 0
}

CONTENT_TITLE_STYLE = {
    'color': '#FFF',
    'font-size': 16,
    'font-weight': 'bold'
}

CONTENT_STYLE = {
    'color': '#AAA',
    'font-size': 14
}

RED = '#e50f04'
GREEN = '#2ffc14'
YELLOW = '#ffc61c'


#################### SIDEBAR ####################
SIDEBAR_STYLE = {
    'width': 250,
    'position': 'fixed',
    'background': '#FFF',
    'height': '100%',
    'margin': 0,
    'padding': 0
}

TITLE_STYLE = {
    'font-size': 24,
    'font-weight': 'bold',
    'margin-top': 8,
    'margin-left': 32,
    'margin-mottom': 12
}

SUBTITLE_STYLE = {
    'font-size': 16,
    'font-weight': 'bold',
    'margin-bottom': -8,
    'margin-left': 32
}

def sidebar_button(text, href):
    return html.Div([dcc.Link(text, href=href, style=SIDEBAR_TEXT_STYLE)], style=SIDEBAR_BUTTON_STYLE)

SIDEBAR = html.Div([
    html.Label('Earth', style=TITLE_STYLE),
    html.Label('Image Classifcation', style=SUBTITLE_STYLE),
    html.Label('Cluster Labeling', style=SUBTITLE_STYLE),
], style=SIDEBAR_STYLE)


#################### MAIN ####################
MAIN_STYLE = {
    'padding-left': 270,
    'padding-top': 20,
    'padding-right': 20,
    'padding-bottom': 20,
    'overflow': 'auto',
    'height': '100%',
    'background': '#111'
}


image_block = html.Div([
    html.Label('Clustering', style=CONTENT_TITLE_STYLE),
    html.Hr(style={'margin-top': 10, 'margin-bottom': 15}),
    html.Div(id='image_block'),
    html.Label('What cluster is the cloud group?', style=CONTENT_STYLE),
    html.Div([
        html.Button('Red Group', id='pause-preproc', style={'width': 200, 'margin-right': 10}),
        html.Button('Green Group', id='pause-preproc', style={'width': 200, 'margin-right': 10}),
        html.Button('Neither Groups', id='pause-preproc', style={'width': 200, 'margin-right': 10}),
        html.Button('Both Groups', id='pause-preproc', style={'width': 200, 'margin-right': 10})
    ], style={'margin-top': 10}),
    html.Button('Bad Clustering', id='pause-preproc', style={'width': 830, 'margin-top': 10})
], style={'margin-bottom': 20})

queue_block = html.Div([
    html.Label('Queued Images', style=CONTENT_TITLE_STYLE),
    html.Hr(style={'margin-top': 10, 'margin-bottom': 15}),
    html.Div(id='queue_block')
])

MAIN = html.Div([image_block, queue_block], id='main', style=MAIN_STYLE)
