import time
import threading

import dash
import dash_core_components as dcc
import dash_html_components as html
import base64

import earth.projects.land_class.cloud_labeling.html_elem as html_elem
from earth.projects.land_class.cloud_labeling.loader import DataLabelLoader


class DataLabeling(object):
    def __init__(self):
        self.loader = DataLabelLoader()
        self.red_button_count = 0
        self.green_button_count = 0
        self.neither_button_count = 0
        self.both_button_count = 0
        self.bad_cluster_button_count = 0
        self.current_lid = None

        self.app = dash.Dash()
        self.app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
        self.app.config['suppress_callback_exceptions']=True
        self.app.layout = self.generate_layout

        self.define_updaters()
        self.run()


    def generate_image_block(self):
        if len(self.loader.processed_outputs.keys()) == 0: return []

        self.current_lid = list(self.loader.processed_outputs.keys())[0]
        data = self.loader.processed_outputs[self.current_lid]
        data['image'].save('image.png')
        encoded_image = base64.b64encode(open('image.png', 'rb').read())
        return [html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))]


    def generate_queue(self):
        return [html.Label(lid, style=html_elem.CONTENT_STYLE) for lid in self.loader.processed_outputs.keys()]


    def generate_layout(self):
        image_block = html.Div([
            html.Label('Clustering', style=html_elem.CONTENT_TITLE_STYLE),
            html.Hr(style={'margin-top': 10, 'margin-bottom': 15}),
            html.Div(self.generate_image_block(), id='image_block'),
            html.Label('What cluster is the cloud group?', style=html_elem.CONTENT_STYLE),
            html.Div([
                html.Button('Red Group', id='red_button', style={'width': 200, 'margin-right': 10}),
                html.Button('Green Group', id='green_button', style={'width': 200, 'margin-right': 10}),
                html.Button('Neither Groups', id='neither_button', style={'width': 200, 'margin-right': 10}),
                html.Button('Both Groups', id='both_button', style={'width': 200, 'margin-right': 10})
            ], style={'margin-top': 10}),
            html.Button('Bad Clustering', id='bad_cluster_button', style={'width': 830, 'margin-top': 10})
        ], style={'margin-bottom': 20})

        queue_block = html.Div([
            html.Label('Queued Images', style=html_elem.CONTENT_TITLE_STYLE),
            html.Hr(style={'margin-top': 10, 'margin-bottom': 15}),
            html.Div(self.generate_queue(), id='queue_block')
        ])

        return html.Div([
            dcc.Interval(id='updater', interval=2000),
            html_elem.SIDEBAR,
            html.Div([image_block, queue_block], id='main', style=html_elem.MAIN_STYLE)
        ], style=html_elem.GLOBAL_STYLE)


    def define_updaters(self):
        @self.app.callback(
            dash.dependencies.Output('queue_block', 'children'),
            events=[dash.dependencies.Event('updater', 'interval')]
        )
        def update_queue():
            return self.generate_queue()

        @self.app.callback(
            dash.dependencies.Output('image_block', 'children'),
            [
                dash.dependencies.Input('red_button', 'n_clicks'),
                dash.dependencies.Input('green_button', 'n_clicks'),
                dash.dependencies.Input('neither_button', 'n_clicks'),
                dash.dependencies.Input('both_button', 'n_clicks'),
                dash.dependencies.Input('bad_cluster_button', 'n_clicks')
            ]
        )
        def cluster_assignment(
            red_button_clicks, green_button_clicks, neither_button_clicks,
            both_button_clicks, bad_cluster_button_clicks
        ):
            if len(self.loader.processed_outputs.keys()) == 0: return []
            if (
                red_button_clicks is None and
                green_button_clicks is None and
                neither_button_clicks is None and
                both_button_clicks is None and
                bad_cluster_button_clicks is None
            ):
                self.red_button_count = 0
                self.green_button_count = 0
                self.neither_button_count = 0
                self.both_button_count = 0
                self.bad_cluster_button_count = 0

            if red_button_clicks is None: red_button_clicks = 0
            if green_button_clicks is None: green_button_clicks = 0
            if neither_button_clicks is None: neither_button_clicks = 0
            if both_button_clicks is None: both_button_clicks = 0
            if bad_cluster_button_clicks is None: bad_cluster_button_clicks = 0

            if red_button_clicks != self.red_button_count:
                self.loader.write_results(self.current_lid, [0])
            elif green_button_clicks != self.green_button_count:
                self.loader.write_results(self.current_lid, [1])
            elif neither_button_clicks != self.neither_button_count:
                self.loader.write_results(self.current_lid, [])
            elif both_button_clicks != self.both_button_count:
                self.loader.write_results(self.current_lid, [0, 1])
            elif bad_cluster_button_clicks != self.bad_cluster_button_count:
                self.loader.write_results(self.current_lid, None)

            self.red_button_count = red_button_clicks
            self.green_button_count = green_button_clicks
            self.neither_button_count = neither_button_clicks
            self.both_button_count = both_button_clicks
            self.bad_cluster_button_count = bad_cluster_button_clicks
            return self.generate_image_block()


    def run(self):
        self.app.run_server(port=8051)


DataLabeling()
