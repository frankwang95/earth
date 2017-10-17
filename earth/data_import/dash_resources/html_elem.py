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

SIDEBAR_BUTTON_STYLE = {
    'width': 100,
    'margin-top': 8,
    'margin-bottom': 8,
    'margin-left': 32
}

SIDEBAR_TEXT_STYLE = {
    'text-decoration': 'none',
    'font-size': 12
}

TITLE_STYLE = {
    'font-size': 24,
    'font-weight': 'bold',
    'margin-top': 8,
    'margin-left': 32
}

SUBTITLE_STYLE = {
    'font-size': 16,
    'font-weight': 'bold',
    'margin-top': -12,
    'margin-bottom': 8,
    'margin-left': 32
}

def sidebar_button(text, href):
    return html.Div([dcc.Link(text, href=href, style=SIDEBAR_TEXT_STYLE)], style=SIDEBAR_BUTTON_STYLE)

SIDEBAR = html.Div([
    html.Label('Earth', style=TITLE_STYLE),
    html.Label('Data Acquisition', style=SUBTITLE_STYLE),
    sidebar_button('Queue', '/queue'),
    sidebar_button('Logs', '/logs'),
    sidebar_button('Status', '/status')
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

MAIN = html.Div(id='main', style=MAIN_STYLE)
