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

app.layout = html.Div(
    children=[

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
    ),

    dcc.DatePickerSingle(
        id='dps_start_date',
        date=datetime.date.today()
    ),
    
    dcc.Input(
        id='dps_start_timetxt',
        placeholder='00:00:00',
        type='text',
        value='00:00:00'
    ),

    dcc.DatePickerSingle(
        id='dps_end_date',
        date=datetime.date.today()
    ),
    
    dcc.Input(
        id='dps_end_timetxt',
        placeholder=datetime.datetime.now().strftime("%H:%M:%S"),
        type='text',
        value='00:00:00',
        disabled = False
    ),  
    dcc.Checklist(
        id="isLiveData",
        options=[
            {'label': 'Live', 'value': 'LiveData'}
        ],
        value=['LiveData']
    ),  
])

@app.callback(
    Output("data-update","interval"),
    [
        Input("isLiveData","value")
    ]
)
def toggle_liveupdate(LiveDataValue):
    if 'LiveData' in LiveDataValue:
        return int(1000)
    else:
        return int(1000*60*24)

@app.callback(
    Output("agraph", "figure"), 
    [
        Input("data-update", "n_intervals"), 
        Input("dps_start_date", "date"),
        Input("dps_start_timetxt", "value"),
        Input("isLiveData", "value")
    ]
)
def gen_data_graph(interval, startdt, starttime, LiveDataValue):
    isLive = False
    if startdt != None and starttime != None:
        t0 = parse_date_timetxt(startdt, starttime)
    else:
        t0 = datetime.datetime.now() - datetime.timedelta(seconds=3600)

    tf = datetime.datetime.now()
    
    data = get_data(t0,tf)
    trace = dict(
        type="scatter",
        x = data["time"],
        y = data["v1"],
        line = {'color':'#F2C417'},
        mode = "lines+markers"
    )
    layout = dict(
        plot_bgcolor=app_color["graph_bg"],
        paper_bgcolor=app_color["graph_bg"],
        font={"color": "#fff"},
        height=700,
        xaxis={
            "showline": False,
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


def parse_date_timetxt(date,timetxt):
    time_h, time_m, time_s = timetxt.split(':')
    dtdate = datetime.datetime.strptime(date.split(' ')[0], '%Y-%m-%d')
    return datetime.datetime(dtdate.year, dtdate.month, dtdate.day, int(time_h), int(time_m), int(time_s))

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

def get_current_time():
    """ Helper function to get the current time in seconds. """
    now = datetime.datetime.now()
    total_time = (now.hour * 3600) + (now.minute * 60) + (now.second)
    return total_time

if __name__ == '__main__':
    app.run_server(debug=True)