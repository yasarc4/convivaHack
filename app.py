# Import required libraries
import pickle
import copy
import pathlib
import dash
import math
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from fbprophet import Prophet
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
import numpy as np
import plotly.graph_objects as go


# Multi-dropdown options
from const import STATES, ASSETS, DEVICES, DEVICE_COLORS

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
state_options = [
    {"label": str(STATES[code]), "value": str(code)} for code in STATES.keys()
]
#well status is asset
asset_options = [
    {"label": str(asset), "value": str(asset)}
    for asset in ASSETS
]
#well type is device
device_options = [
    {"label": str(device), "value": str(device)}
    for device in DEVICES
]


# Load data
df = pd.read_csv(DATA_PATH.joinpath("simpleSS.csv"), low_memory=False)
nw = pd.datetime.now()
df["ts"] = df.ts.apply(lambda x: nw - pd.Timedelta('{} m'.format(x-20)))
ts = df.ts.astype(int)
min_ts = ts.min()
max_ts = ts.max()

# Create global chart template
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    ),
)

# Create app layout
app.layout = html.Div(
    [
        # dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("conviva-logo2.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Live Insights",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Overview of the live Assets", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://pulse.conviva.com/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by Timestamp (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=min_ts,
                            max=max_ts + 60*1e9*10,
                            step=60*1e9,
                            value=[min_ts, max_ts],
                            className="dcc_control",
                        ),
                        html.P("Filter by Asset:", className="control_label"),
                        dcc.RadioItems(
                            id="asset_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Live ", "value": "live"},
                                {"label": "Recorded ", "value": "recorded"},
                            ],
                            value="active",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="assetes",
                            options=asset_options,
                            multi=True,
                            value=list(ASSETS),
                            className="dcc_control",
                        ),
                        dcc.Checklist(
                            id="lock_selector",
                            options=[{"label": "Lock camera", "value": "locked"}],
                            className="dcc_control",
                            value=[],
                        ),
                        html.P("Filter by Device:", className="control_label"),
                        dcc.RadioItems(
                            id="device_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "TV Only ", "value": "tv"},
                                {"label": "Other Devices ", "value": "other"},
                            ],
                            value="productive",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="devices",
                            options=device_options,
                            multi=True,
                            value=list(DEVICES),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="playText"), html.P("Max of Concurrent Plays")],
                                    id="Plays",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="sessionText"), html.P("Avg. Session Time")],
                                    id="Sessions",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="rbrText"), html.P("Avg. RbR")],
                                    id="Rbr",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="assetText"), html.P("Number of Live Assets")],
                                    id="Assets",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="count_graph")],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),

        html.Div(
            [
                html.Div([dcc.Graph(id='us_map')], className="pretty_container seven columns"),
                html.Div([dcc.Graph(id='three_pct')], className="pretty_container five columns"),
            ],
            className="row flex-display"
        ),
        
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Helper functions
def human_format(num):
    if num == 0:
        return "0"

    magnitude = int(math.log(num, 1000))
    mantissa = str(int(num / (1000 ** magnitude)))
    return mantissa + ["", "K", "M", "G", "T", "P"][magnitude]


def filter_dataframe(df, assets, devices, year_slider):
    dff = df[
        df["asset"].isin(assets)
        & df["device"].isin(devices)
        & (df["ts"] > pd.to_datetime(int(year_slider[0]/1e9), unit='s'))
        & (df["ts"] < pd.to_datetime(int(year_slider[1]/1e9), unit='s'))
    ]
    return dff


def produce_individual(api_well_num):
    try:
        points[api_well_num]
    except:
        return None, None, None, None

    index = list(
        range(min(points[api_well_num].keys()), max(points[api_well_num].keys()) + 1)
    )
    gas = []
    oil = []
    water = []

    for year in index:
        try:
            gas.append(points[api_well_num][year]["Gas Produced, MCF"])
        except:
            gas.append(0)
        try:
            oil.append(points[api_well_num][year]["Oil Produced, bbl"])
        except:
            oil.append(0)
        try:
            water.append(points[api_well_num][year]["Water Produced, bbl"])
        except:
            water.append(0)

    return index, gas, oil, water


def produce_aggregate(selected, year_slider):

    index = list(range(max(year_slider[0], 1985), 2016))
    gas = []
    oil = []
    water = []

    for year in index:
        count_gas = 0
        count_oil = 0
        count_water = 0
        for api_well_num in selected:
            try:
                count_gas += points[api_well_num][year]["Gas Produced, MCF"]
            except:
                pass
            try:
                count_oil += points[api_well_num][year]["Oil Produced, bbl"]
            except:
                pass
            try:
                count_water += points[api_well_num][year]["Water Produced, bbl"]
            except:
                pass
        gas.append(count_gas)
        oil.append(count_oil)
        water.append(count_water)

    return index, gas, oil, water


# Create callbacks
app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("count_graph", "figure")],
)


# @app.callback(
#     Output("aggregate_data", "data"),
#     [
#         Input("assetes", "value"),
#         Input("devices", "value"),
#         Input("year_slider", "value"),
#     ],
# )
# def update_production_text(assetes, devices, year_slider):
#
#     dff = filter_dataframe(df, assetes, devices, year_slider)
#     selected = dff["ts"].values
#     index, gas, oil, water = produce_aggregate(selected, year_slider)
#     return [human_format(sum(gas)), human_format(sum(oil)), human_format(sum(water))]


# Radio -> multi
@app.callback(
    Output("assetes", "value"), [Input("asset_selector", "value")]
)
def display_status(selector):
    if selector == "all":
        return list(ASSETS)
    elif selector == "active":
        return [i  for i in ASSETS if 'LIVE' in i]
    return [i  for i in ASSETS if 'RECORDED' in i]


# Radio -> multi
@app.callback(Output("devices", "value"), [Input("device_selector", "value")])
def display_type(selector):
    if selector == "all":
        return list(DEVICES)
    elif selector == "tv":
        return [i  for i in DEVICES if 'TV' in i]
    return [i  for i in DEVICES if 'TV' not in i]


# Slider -> count graph
@app.callback(Output("year_slider", "value"), [Input("count_graph", "selectedData")])
def update_year_slider(count_graph_selected):

    if count_graph_selected is None:
        return [min_ts, max_ts+1]

    nums = [int(point["pointNumber"]) for point in count_graph_selected["points"]]
    return [min(nums)*60 + min_ts, max(nums)*60 + min_ts]


# Selectors -> well text
@app.callback(
    Output("playText", "children"),
    [
        Input("assetes", "value"),
        Input("devices", "value"),
        Input("year_slider", "value"),
    ],
)
def update_well_text(assetes, devices, year_slider):

    dff = filter_dataframe(df, assetes, devices, year_slider)
    return dff.groupby('ts')['concurrentPlays'].sum().max()


@app.callback(
    [
        Output("sessionText", "children"),
        Output("rbrText", "children"),
        Output("assetText", "children"),
    ],
    [Input("assetes", "value"),
    Input("devices", "value"),
    Input("year_slider", "value")],
)
def update_text(assetes, devices, year_slider):
    dff = filter_dataframe(df, assetes, devices, year_slider)
    return '{} mins'.format(round(dff.sessionLength.mean(),2)), '{}%'.format(round(dff.rbr.mean(),2)), dff[dff.concurrentPlays>0].asset.nunique()


@app.callback(
    Output("three_pct", "figure"),
    [
        Input("assetes", "value"),
        Input("devices", "value"),
        Input("year_slider", "value"),
    ],
)
def plot_multiline(assetes, devices, year_slider):
    dff = filter_dataframe(df, assetes, devices, year_slider)
    data = [
            dict(
                type="scatter",
                mode="lines",
                name="RbR%",
                x=dff['ts'],
                y=dff['rbr'],
                line=dict(shape="spline", smoothing="2", color="#F9ADA0"),
            ),
            dict(
                type="scatter",
                mode="lines",
                name="VSF%",
                x=dff['ts'],
                y=dff['isVsf'],
                line=dict(shape="spline", smoothing="2", color="#849E68"),
            ),
            dict(
                type="scatter",
                mode="lines",
                name="EBVS%",
                x=dff['ts'],
                y=dff['isEbvs'],
                line=dict(shape="spline", smoothing="2", color="#59C3C3"),
            ),
        ]
    layout={'title': 'Play Metrics'}
    return dict(data=data, layout=layout)

@app.callback(
    Output("us_map", "figure"),
    [
        Input("assetes", "value"),
        Input("devices", "value"),
        Input("year_slider", "value"),
    ],
)
def plot_map(assetes, devices, year_slider):
    dff = filter_dataframe(df, assetes, devices, year_slider)
    data = dict(data=go.Choropleth(
        locations=dff['state'], # Spatial coordinates
        z = dff['justJoined'].astype(float), # Data to be color-coded
        locationmode = 'USA-states', # set of locations match entries in `locations`
        colorscale = 'Reds',
        colorbar_title = "Num Sessions",
    ))

    layout=dict(
        title_text = 'New Sessions by State',
        geo_scope='usa', # limite map scope to USA
    )

    return go.Figure(data=data, layout=layout)

# Selectors -> count graph
@app.callback(
    Output("count_graph", "figure"),
    [
        Input("assetes", "value"),
        Input("devices", "value"),
        Input("year_slider", "value"),
    ],
)
def make_count_figure(assetes, devices, year_slider):
    layout_count = copy.deepcopy(layout)
    dff = filter_dataframe(df, assetes, devices, year_slider)
    p_df = dff.groupby('ts')['justJoined'].sum().reset_index()
    p_df.columns = ['ds','y']
    model = Prophet()
    model.fit(p_df)
    f_df = model.make_future_dataframe(10,freq='min', include_history=False)
    f_df = model.predict(f_df)[['ds','yhat']]

    try:
        amodel = ARIMA(p_df.y, order=(2,0,1))
        model_fit = amodel.fit(disp=0)
        arima_pred = model_fit.predict(len(p_df), len(p_df)+9)
    except:
        amodel = SARIMAX(p_df.y, order=(2,1,1), enforce_invertibility=False, enforce_stationarity=False)
        model_fit = amodel.fit(disp=0)
        arima_pred = model_fit.predict(len(p_df), len(p_df)+9)
    f_df.yhat = (f_df.yhat.values+arima_pred.values)/2
    g = pd.concat([dff.groupby('ts')['justJoined'].sum(), f_df.set_index('ds')['yhat']])
    colors = []
    for i in range(int(min_ts), int(max_ts+10*60*1e9+1), int(60*1e9)):
        if (i>max_ts):
            colors.append("rgb(100,20,20,0.3)")
        elif (i >= int(year_slider[0])) and (i < int(year_slider[1]+1)):
            colors.append("rgb(123, 199, 255)")
        else:
            colors.append("rgba(123, 199, 255, 0.2)")
    data = [
        dict(
            type="scatter",
            mode="markers",
            x=list(g.index),
            y=g,
            name="Number Attempts",
            opacity=0,
            hoverinfo="skip",
        ),
        dict(
            type="bar",
            x=g.index,
            y=g,
            name="Number Attempts",
            marker=dict(color=colors),
        ),
    ]

    layout_count["title"] = "Number of Attempts"
    layout_count["dragmode"] = "select"
    layout_count["showlegend"] = False
    layout_count["autosize"] = True

    figure = dict(data=data, layout=layout_count)
    return figure


# Main
if __name__ == "__main__":
    app.run_server(debug=True)
