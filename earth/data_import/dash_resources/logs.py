import dash_core_components as dcc
import dash_html_components as html


LOG_STYLE = {
    'width': '100%'
}

LOG_TEXT_STYLE = {
    'color': '#999',
    'font-size': '10px',
    'padding-left': 20
}

def create_log_table(logs):
    return [html.Tr([html.Td(log, style=LOG_TEXT_STYLE)]) for log in logs]


layout = [
    html.Table(id='log_table', style=LOG_STYLE)
]
