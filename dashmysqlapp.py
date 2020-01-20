import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import pymysql
import pymysql.cursors
import datetime
import numpy as np
import pandas as pd

GRAPH_INTERVAL = 1000
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app_color = {"graph_bg": "#082255", "graph_line": "#007ACE"}

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    dcc.Graph(
        id="agraph",
        figure=dict(
            layout=dict(
                plot_bgcolor=app_color["graph_bg"],
                paper_bgcolor=app_color["graph_bg"],
            )
        ),
    ),
    dcc.Interval(
        id="data-update",
        interval=int(GRAPH_INTERVAL),
        n_intervals=0,
    )
])

def get_current_time():
    """ Helper function to get the current time in seconds. """
    now = datetime.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + (now.second)
    return total_time

@app.callback(
    Output("agraph", "figure"), [Input("data-update", "n_intervals")]
)
def gen_data_graph(interval):
    t0 = datetime.datetime.now() - datetime.timedelta(seconds=3600)
    tf = datetime.datetime.now()
    data = get_data(t0,tf)
    trace = dict(
        type="scatter",
        x = data["time"],
        y = data["v1"],
        line = {'color':'#42C4F7'},
        mode = "lines"
    )
    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=700,
        xaxis={
            "showline": True,
            "title": "Time",
        },
        yaxis={
            "range": [
                min(data["v1"]),
                max(data["v1"]),
            ],
            "showgrid": True,
            "showline": True,
            "fixedrange": True,
            "zeroline": False,
            "gridcolor": app_color["graph_line"],
            "nticks": max(6, round(data["v1"].iloc[-1] / 10)),
        },
    )
    return dict(data=[trace], layout=layout)


def get_data(t0,tf):
    if type(t0) == datetime.datetime:
        t0 = t0.strftime('%Y-%m-%d %H:%M:%S')
    if type(tf) == datetime.datetime:
        tf = tf.strftime('%Y-%m-%d %H:%M:%S')
    sql = "SELECT * FROM testtable WHERE time > '%s' AND time < '%s'"%(t0,tf)
    connection = get_db_conn_read()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
    finally:
        connection.close()
    return pd.DataFrame(data)

def get_db_conn_read():
    connection = pymysql.connect(
                    host='127.0.0.1',
                    user='exo_ro',
                    password='xenon',
                    db='lab206',
                    port=3308,
                    cursorclass=pymysql.cursors.DictCursor)
    return connection

if __name__ == '__main__':
    app.run_server(debug=True)