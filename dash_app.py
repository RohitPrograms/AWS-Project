# pull-quotes lambda function code (DO NOT CHANGE)
# 

import dash
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import mysql.connector
from mysql.connector import Error
import pandas as pd
import plotly.express as px
import datetime



def get_futures_date(futures_symbol):
    futures_dict = {
        'F': 1,
        'G': 2,
        'H': 3,
        'J': 4,
        'K': 5,
        'M': 6,
        'N': 7,
        'Q': 8,
        'U': 9,
        'V': 10,
        'X': 11,
        'Z': 12
    }

    dt = datetime.datetime(year = 2000 + int(futures_symbol[4:]),
                month = futures_dict[futures_symbol[3]],
                day = 1,
                hour = 0,
                minute = 0,
                second = 0
            )
    return dt


# Create a Dash app
app = dash.Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id='cl-futures-curve')
        ], style={'flex': '1', 'padding': '10px'}),  # First graph

        html.Div([
            dcc.Graph(id='ng-futures-curve')
        ], style={'flex': '1', 'padding': '10px'})  # Second graph
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),

    dcc.Interval(
        id='interval-component',
        interval=60000,  # Update interval in milliseconds (60000 ms = 1 min)
        n_intervals=0
    )
])

    # dcc.Graph(id = 'cl-futures-curve'),
    # dcc.Graph(id = 'ng-futures-curve'),


# Callback to /CL futures curve
@app.callback(
    Output('cl-futures-curve', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_CL_futures_graph(n_intervals):
    MySQL_connection = None

    # connecting to RDS instances seems to have super transient network issues
    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        try:
            host = "your AWS RDS database"
            user = "username"
            password = "password"
            MySQL_connection = mysql.connector.connect(user = user, password = password, host = host, database = 'project_data')

            if MySQL_connection.is_connected():

                cursor = MySQL_connection.cursor()

                cursor.execute('SELECT * FROM quotes WHERE symbol LIKE "/CL%" AND quoteTime = (SELECT quoteTime FROM quotes WHERE symbol LIKE "/CL%" ORDER BY id DESC LIMIT 1)')
                columns = [col[0] for col in cursor.description]
                df = pd.DataFrame(cursor.fetchall(), columns=columns)
                MySQL_connection.close()

                df['date'] = df.apply(lambda row: get_futures_date(row['symbol']), axis = 1)
                df= df.sort_values(by = 'date')

                fig = px.line(data_frame = df, x = 'date', y = 'askPrice', markers = True, text = 'askPrice', color_discrete_sequence=['blue'],
                            width = 1000, height = 500,
                            title = 'WTI Crude Oil Futures',
                            labels = {
                                "date": "Contract",
                                "askPrice": "Ask Price"
                            }
                            )

                fig.update_traces(textposition = 'top center')

                fig.update_layout(
                    plot_bgcolor='white', 
                    paper_bgcolor='white', 
                    

                    xaxis = dict(
                        showline=True,
                        linecolor = 'black',
                        linewidth = 2,
                        showgrid = False,
                        ticks = 'inside'
                    ),

                    yaxis = dict(
                        showline=True,
                        linecolor = 'black',
                        linewidth = 2,
                        showgrid = True,
                        gridcolor='LightGray',
                        gridwidth=1  
                    )
                )

                fig.update_xaxes(
                    tickvals = df['date'],  # Custom tick values
                    ticktext = df['date'].apply(lambda x :x.strftime("%b '%y"))
                )

                return fig


        except Error as e:
            attempt += 1
    
    return None

# Callback to /NG futures curve
@app.callback(
    Output('ng-futures-curve', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_NG_futures_graph(n_intervals):
    MySQL_connection = None

    # connecting to RDS instances seems to have super transient network issues
    max_retries = 10
    attempt = 0

    while attempt < max_retries:
        try:
            host = "your AWS RDS database"
            user = "username"
            password = "password"
            MySQL_connection = mysql.connector.connect(user = user, password = password, host = host, database = 'project_data')

            if MySQL_connection.is_connected():

                cursor = MySQL_connection.cursor()

                cursor.execute('SELECT * FROM quotes WHERE symbol LIKE "/NG%" AND quoteTime = (SELECT quoteTime FROM quotes WHERE symbol LIKE "/NG%" ORDER BY id DESC LIMIT 1)')
                columns = [col[0] for col in cursor.description]
                df = pd.DataFrame(cursor.fetchall(), columns=columns)
                MySQL_connection.close()

                df['date'] = df.apply(lambda row: get_futures_date(row['symbol']), axis = 1)
                df= df.sort_values(by = 'date')

                fig = px.line(data_frame = df, x = 'date', y = 'askPrice', markers = True, text = 'askPrice', color_discrete_sequence=['blue'],
                            width = 1000, height = 500,
                            title = 'Henry Hub Natural Gas Futures',
                            labels = {
                                "date": "Contract",
                                "askPrice": "Ask Price"
                            }
                            )

                fig.update_traces(textposition = 'top center')

                fig.update_layout(
                    plot_bgcolor='white', 
                    paper_bgcolor='white', 
                    

                    xaxis = dict(
                        showline=True,
                        linecolor = 'black',
                        linewidth = 2,
                        showgrid = False,
                        ticks = 'inside'
                    ),

                    yaxis = dict(
                        showline=True,
                        linecolor = 'black',
                        linewidth = 2,
                        showgrid = True,
                        gridcolor='LightGray',
                        gridwidth=1  
                    )
                )

                fig.update_xaxes(
                    tickvals = df['date'],  # Custom tick values
                    ticktext = df['date'].apply(lambda x :x.strftime("%b '%y"))
                )

                return fig


        except Error as e:
            attempt += 1
    
    return None

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
