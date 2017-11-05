import time
import threading

import dash
import dash_core_components as dcc
import dash_html_components as html

from earth.data_import.landsat.scheduler import Scheduler
import earth.data_import.landsat.dash_resources.html_elem as html_elem
import earth.data_import.landsat.dash_resources.logs as logs
import earth.data_import.landsat.dash_resources.queue as queue
import earth.data_import.landsat.dash_resources.status as status


sched = Scheduler()
app = dash.Dash()
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.config['suppress_callback_exceptions']=True
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(
        id='updater',
        interval=500
    ),
    html_elem.SIDEBAR,
    html_elem.MAIN
], style=html_elem.GLOBAL_STYLE)


@app.callback(
    dash.dependencies.Output('main', 'children'),
    [dash.dependencies.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname=='/logs': return logs.layout
    if pathname=='/queue': return queue.layout
    if pathname=='/status': return status.layout


@app.callback(
    dash.dependencies.Output('log_table', 'children'),
    events=[dash.dependencies.Event('updater', 'interval')]
)
def log_updater():
    with open('logs/{}'.format(sched.log_name), 'r') as f:
        return logs.create_log_table(f.readlines()[:500])


@app.callback(
    dash.dependencies.Output('shutdown', 'children'),
    [dash.dependencies.Input('shutdown', 'n_clicks')]
)
def shutdown_main(n_clicks):
    if n_clicks > 0: sched.shutdownT = True
    return 'Shutdown'


@app.callback(
    dash.dependencies.Output('pause-master', 'style'),
    [dash.dependencies.Input('pause-master', 'n_clicks')],
    events=[dash.dependencies.Event('updater', 'interval')]
)
def master_pause(pause_n_clicks):
    if sched.shutdownT: return {'width': 600, 'color': html_elem.RED}
    if pause_n_clicks is not None: sched.pausedT = pause_n_clicks % 2 != 0

    if sched.pausedT: return {'width': 600, 'color': html_elem.YELLOW}
    return {'width': 600, 'color': html_elem.GREEN}


@app.callback(
    dash.dependencies.Output('pause-preproc', 'style'),
    [dash.dependencies.Input('pause-preproc', 'n_clicks')],
    events=[dash.dependencies.Event('updater', 'interval')]
)
def shutdown_preproc_pause_switch(pause_n_clicks):
    if sched.shutdownPreprocT: return {'width': 295, 'color': html_elem.RED}
    if pause_n_clicks is not None: sched.pausedPreprocT = pause_n_clicks % 2 != 0

    if sched.pausedPreprocT: return {'width': 295, 'color': html_elem.YELLOW}
    return {'width': 295, 'color': html_elem.GREEN}


@app.callback(
    dash.dependencies.Output('pause-download', 'style'),
    [dash.dependencies.Input('pause-download', 'n_clicks')],
    events=[dash.dependencies.Event('updater', 'interval')]
)
def shutdown_download_pause_switch(pause_n_clicks):
    if sched.shutdownDownloadT: return {'width': 295, 'color': html_elem.RED, 'margin-left': 10}
    if pause_n_clicks is not None: sched.pausedDownloadT = pause_n_clicks % 2 != 0

    if sched.pausedDownloadT: return {'width': 295, 'color': html_elem.YELLOW, 'margin-left': 10}
    return {'width': 295, 'color': html_elem.GREEN, 'margin-left': 10}


#################### MAIN ####################
app.run_server()