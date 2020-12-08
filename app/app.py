import dash
from dash.dependencies           import Input, Output, State
from dash.exceptions             import PreventUpdate
from myfuncs                     import * 
import dash_core_components      as dcc
import dash_html_components      as html
import dash_bootstrap_components as dbc
import dash_table                as dt
import pandas                    as pd
import numpy                     as np
import geopandas                 as gpd
import plotly.express            as px
import plotly.graph_objects      as go
import plotly.figure_factory     as ff

import flask
import os
import datetime

# read the data
facilities_db = pd.read_csv(
    '../cleaned-data/manhattan-surroundings_cleaned.csv', 
    dtype = {'zipcode':str},
    index_col = 0
)

facilities_db = facilities_db.rename(columns = {'nta':'ntacode'})
crime_geom = pd.read_csv('../cleaned-data/manhattan-crimes_data-cleaned.csv', parse_dates = ['datetime'])
crime_count = crime_geom.groupby(['ntaname', 'latitude', 'longitude']).size().to_frame('count').reset_index()
crime_count = crime_count.sort_values(by = 'count', ascending = False).reset_index(drop = True)
crime_count = crime_count.rename(columns = {'latitude':'lat', 'longitude':'lon'})

nyc_ntas = gpd.read_file('../raw-data/nyc-TNA.geojson', driver = "GeoJSON")

lower_manhattan = ['Clinton', 
                   'Midtown-Midtown South', 
                   'Turtle Bay-East Midtown', 
                   'Murray Hill-Kips Bay', 
                   'Hudson Yards-Chelsea-Flatiron-Union Square',
                   'Gramercy',
                   'Stuyvesant Town-Cooper Village',
                   'East Village',
                   'West Village',
                   'Lower East Side',
                   'Chinatown',
                   'SoHo-TriBeCa-Civic Center-Little Italy',
                   'Battery Park City-Lower Manhattan'
                  ]

# lower_manhattan_geom = nyc_ntas[nyc_ntas['ntaname'].isin(lower_manhattan)]
lower_manhattan_geom = nyc_ntas.copy()

rental_df = pd.read_csv('../cleaned-data/manhattan-rental_cleaned.csv', dtype = {'zipcode':str})
rental_df = gpd.GeoDataFrame(
    rental_df, 
    geometry = gpd.points_from_xy(
        rental_df.longitude, 
        rental_df.latitude
        )
)
rental_df.crs = {'init': 'epsg:4326'}
rental_df = gpd.sjoin(
    left_df = rental_df, 
    right_df = lower_manhattan_geom[['geometry', 'ntacode', 'ntaname']], 
    how = 'inner'
)

cols = ['ntaname', 'zipcode', 'name', 'address', 'contact', 'rating', 'type', 'price']
df = rental_df[cols].sort_values(by = ['price', 'rating'], ascending = [True, False])

yelp_data = pd.read_csv('../cleaned-data/yelp-restaurants_cleaned.csv', dtype = {'Zipcode':str})
yelp_cols = ['restaurant name', 'business address', 'food types', 'rating']

# helpers
zipcodes = sorted(list(rental_df['zipcode'].unique()))
facilities = sorted(list(facilities_db['facgroup'].unique()))
rental_types = ['Studio', '1 Bedroom', '2 Bedrooms', '3 Bedrooms', '4+ Bedrooms']

# authentication
users = {'admin':'123456', 'user1':'555478'}

# controls
zipcode_opts = [{'label': zipcode, 'value': zipcode} for zipcode in zipcodes]
facilities_opts = [{'label': fac, 'value': fac} for fac in facilities]
rental_opts = [{'label': rtype, 'value': rtype} for rtype in rental_types]
prices_opts = np.linspace(start = 0, stop = 30000, num = 6)
prices_marks = {int(i): ('${:,.0f}'.format(i)) for i in prices_opts}

# cover page
index = html.Div(
    html.Div([
        # Username
        dbc.InputGroup([
            dbc.InputGroupAddon('@', addon_type = "prepend"),
            dbc.Input(placeholder = "Username", id = 'username'),
            ],
            className = 'dist_log'
            ),

            # Password
            dbc.InputGroup([
                dbc.InputGroupAddon("**", addon_type = "prepend"),
                dbc.Input(placeholder = "Password", id = 'password', type = "password"),
                ],
                className = 'dist_log'
                ),
                # Log Button
                dbc.Button(
                    "Login", 
                    color = "success", 
                    disabled = False, 
                    className = "button",
                    id = 'login_button'
                ),
                
                # Error Message (if applicable)
                html.P(children = '.', id = 'error_log', className = 'error_message')
            ], 
            className = 'login'
            ),
            
            className = 'cover'
)

# top navigation bar
side_nav = html.Div([
    dbc.Nav([
        dbc.Container([
            dbc.NavItem([
                dbc.NavLink([
                    html.Img(
                        src = 'https://www.flaticon.com/svg/static/icons/svg/602/602276.svg',
                        className = 'icons_nav'),
                        '  ', "MZM Rental Recommendations"
                        ],
                        href = "/recommendations", id = "page-1")
                        ])                
                    ])
            ],
            className = 'navbar navbar-expand-lg navbar-dark bg-primary',
            fill = True,
            pills = True
            )
])

user_opts = dbc.Container(
    dbc.Card(
        dbc.CardBody([
            dbc.Row(dbc.Col(html.H4('Just imagine your dream home...', className = "card-title"))),

            dbc.Row(dbc.Col(html.B('What is your monthly budget?'))),

            dbc.Row(
                dbc.Col(
                    dcc.RangeSlider(
                        id = 'price_range',
                        marks = prices_marks,
                        min = 0, 
                        max = 30000,
                        step = 100,
                        value = [1300, 4500],
                        allowCross = False,
                        tooltip = {'always_visible':False}
                    )
                )
            ),

            html.Br(),
            
            dbc.Row(dbc.Col(html.B('What zip code(s) are you interested in?'))),

            # zip codes
            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id = 'zipcodes',
                        options = zipcode_opts,
                        multi = True,
                        value = zipcodes[0],
                        placeholder = 'Select at least one zip code',
                        className = 'p1_options'
                    )
                )
            ),
            
            html.Br(),
            
            dbc.Row(dbc.Col(html.B('What type of rental are you looking for?'))),

            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id = 'rental_types',
                        options = rental_opts,
                        multi = True,
                        value = '2 Bedrooms',
                        placeholder = 'Select one rental type',
                        className = 'p1_options'
                    )
                )
            ),

             html.Br(),

            # facilities
            dbc.Row(dbc.Col(html.B('What places is important for you to be close to?'))),
            dbc.Row(dbc.Col(html.P('Do you want to be close to cultural places? health care centers? restaurants? Name it.'))),

            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id = 'facilities',
                        options = facilities_opts,
                        multi = False,
                        value = 'Health care',
                        placeholder = 'Preference one',
                        className = 'p1_options'
                    )
                )
            ),

            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id = 'facilities2',
                        options = facilities_opts,
                        multi = False,
                        value = 'Transportation',
                        placeholder = 'Preference two',
                        className = 'p1_options'
                    )
                )
            ),

            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id = 'facilities3',
                        options = facilities_opts,
                        multi = False,
                        value = 'Cultural institutions',
                        placeholder = 'Preference three',
                        className = 'p1_options'
                    )
                )
            ),
            
            html.Br(),

            dbc.Row(dbc.Col(html.B('What other specifications are you looking for?'))),
            
            dbc.Row(dbc.Col(html.P('Laundry:'))),

            dbc.Row(
                dbc.Col(
                    dbc.RadioItems(
                        id = 'laundry',
                        options = [
                            {'label': 'No laundry', 'value': 0},
                            {'label': 'Laundry Facilities', 'value': 1},
                            {'label': 'Washer/Dryer In Unit', 'value': 2}
                            ],
                            value = 0,
                            inline = False,
                            labelCheckedStyle = {'font-weight': 'bold'},
                            inputStyle = {"margin-bottom": "10px"}
                    )
                )
            ),

            dbc.Row(dbc.Col(html.P('Parking:'))),

            dbc.Row(
                dbc.Col(
                    dbc.RadioItems(
                        id = 'parking',
                        options = [
                            {'label': 'Yes', 'value': 1},
                            {'label': 'No', 'value': 0}
                            ],
                            value = 0,
                            inline = False,
                            labelCheckedStyle = {'font-weight': 'bold'},
                            inputStyle = {"margin-bottom": "10px"}
                    )
                )
            ),

            dbc.Row(dbc.Col(html.P('Pets allowed:'))),

            dbc.Row(
                dbc.Col(
                    dbc.RadioItems(
                        id = 'pets',
                        options = [
                            {'label': 'Yes', 'value': 1},
                            {'label': 'No', 'value': 0}
                            ],
                            value = 0,
                            inline = False,
                            labelCheckedStyle = {'font-weight': 'bold'},
                            inputStyle = {"margin-bottom": "10px"}
                    )
                )
            ),

            # gerenate recommendations button
            html.Br(),
            dbc.Button("Generate Recommendations", color="primary", id='generate_button'),

            # no results alert
            html.Br(),
            html.Br(),
            dbc.Alert(
                id = 'no-results-alert',
                dismissable = True,
                is_open = False,
                color = 'danger'
                )
        ])
    )
)

recommendations = dbc.Container([
    # row of cards
    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Total No. of Rentals"),
                dbc.CardBody(html.P(id = 'total_no_rentals', className = 'labelcard'))
                    ],
                color = 'dark', inverse = True
                ),
            width = {'size': 6}
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardHeader("Total No. of Results"),
                dbc.CardBody(html.P(id = 'selected_rentals', className = 'labelcard'))
                    ],
                color = 'primary', inverse = True
                ),
            width = {'size': 6}
        )
    ]),
    
    # avg. distance to points of interest
    html.Br(),
    dbc.Row([
        dbc.Col(
            html.Img(
            src = "https://www.flaticon.com/svg/static/icons/svg/3754/3754360.svg",
            style = {'height':'100%', 'width':'100%'}
            ),
            width = {'size': 1}
        ),
        dbc.Col(html.H4('Average distance to points of interest for top recommendation', style = {'vertical-align':'middle'}), 
        width = {'size': 11}
        )
    ],
    style = {'height':'75%'}
    ),

    dbc.Row([
        dbc.Col(
            dbc.Card([
                dbc.CardBody(html.P(id = 'avg-dist-first'))
                    ],
                color = 'primary', inverse = True
                ),
            width = {'size': 4}
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody(html.P(id = 'avg-dist-second'))
                    ],
                color = 'primary', inverse = True
                ),
            width = {'size': 4}
        ),
        dbc.Col(
            dbc.Card([
                dbc.CardBody(html.P(id = 'avg-dist-third'))
                    ],
                color = 'primary', inverse = True
                ),
            width = {'size': 4}
        )
    ]),
    
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4('Location of top recommendation'),
                    html.Iframe(
                        id = 'map',
                        style = {'border': 'none', 'width': '100%', 'height': 350},
                        srcDoc = open('./maps/mymap.html', 'r').read(),
                    ),

                    html.Br(),
                    html.Br(),
                    html.H5('Rental recommendations (ordered from best to worst):'),
                    dt.DataTable(
                        id = 'table',
                        columns = [{'name': i, 'id': i} for i in df.columns],
                        data = df.to_dict('records'),
                        style_cell = {'fontSize': 12, 'font-family':'sans-serif'},
                        style_cell_conditional=[
                            {'if': {'column_id': c}, 'textAlign': 'left'} for c in ['name', 'address']
                        ],
                        style_data_conditional = [
                            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                        ],
                        style_header = {'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'textAlign': 'center'},
                        page_size = 5
                    )]
                )
            ),
            width = {'size': 12}
        )
    ])
])

yelp = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.Card(    
                dbc.CardBody([
                    html.B('Average rating by food type and food level'),
                    dcc.Graph(id = 'type-price-rating')
                    ])
            ),
            width = {'size': 5}
        ),

        dbc.Col(
            dbc.Card(
                dbc.CardBody(
                    dt.DataTable(
                        id = 'yelp-table',
                        columns = [{'name': i, 'id': i} for i in yelp_cols],
                        data = yelp_data.drop_duplicates(subset = 'restaurant name').to_dict('records'),
                        style_cell = {'fontSize': 12, 'font-family':'sans-serif'},
                        style_cell_conditional=[
                            {'if': {'column_id': c}, 'textAlign': 'left'} for c in ['restaurant name', 'business address']
                        ],
                        style_data_conditional = [
                            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(248, 248, 248)'}
                        ],
                        style_header = {'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold', 'textAlign': 'center'},
                        page_size = 10
                    )
                    )
            ),
            width = {'size': 7}
        )
    ])
])

rentals = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id = 'price-histogram')
                ])
            ),
            width = {'size': 4}            
        ),

        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    dcc.Graph(id = 'price-type')
                ])
            ),
            width = {'size': 8}            
        )
        
    ])
])

crime = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.B('Results by Neighborhood Tabular Areas (NTA)'),
                    html.Iframe(
                        id = 'nta-map',
                        style = {'border': 'none', 'width': '100%', 'height': 300},
                        srcDoc = open('./maps/nta_crime_count.html', 'r').read()
                    )
                ])
            ),
            width = {'size': 4}            
        ),

        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.B('Results by level of offense and hour'),
                    dcc.Graph(id = 'crimes-by-hour')
                ])
            ),
            width = {'size': 4}            
        ),

        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.B('Results by level of offense and day'),
                    dcc.Graph(id = 'crimes-by-day')
                ])
            ),
            width = {'size': 4}            
        )
        
    ])
])

# Join up pages
page_1 = html.Div([
    dbc.Row([
        dbc.Col(user_opts, width = {'size': 4, 'offset': 0}),
        dbc.Col(recommendations, width = {'size': 8})
    ],
    className = 'content'
    ),

    dbc.Row([
        html.H4('Nearby Restaurants Info by Zipcode of Top Recommendation'),
        dbc.Col(yelp, width = {'size': 12, 'offset': 0})
    ],
    className = 'content'
    ),
    
    dbc.Row([
        html.H4('Prices of Rentals by NTA of Top Recommendation'),
        dbc.Col(rentals, width = {'size': 12, 'offset': 0})
    ],
    className = 'content'
    ),

    dbc.Row([
        html.H4('Crime Rates Report'),
        dbc.Col(crime, width = {'size': 12, 'offset': 0})
    ],
    className = 'content'
    )   
])

# run the app
theme = 'assets//bootstrap.css'
app = dash.Dash(__name__)
server = app.server
app.config["suppress_callback_exceptions"] = True
app.css.config.serve_locally = False

# active page
app.layout = html.Div([dcc.Location(id = "url"), html.Div(id = "page-content")])  

# index cover
@app.callback(
    [Output("error_log", "children"), Output("url", "pathname")],
    [Input("login_button", 'n_clicks')],
    [State("username", "value"), State("password", "value")]
    )
def index_validation(n_clicks, user, password):

    if (user is None) or (password is None) :
        return '', dash.no_update

    elif user in users.keys():
        if users[user] == password:
            return 'Correct password', "/recommendations"
        else:
            return 'Incorrect password. Check password and try again', dash.no_update
    else: 
        return 'User does not exist. Check username and try again', dash.no_update

# navigation in the dashboard
@app.callback(
    Output("page-content", "children"), 
    Input("url", "pathname")
    )
def render_page_content(pathname):
    if (pathname in ["/", "/index"]):
        return index
    elif (pathname == "/recommendations"):
        return [side_nav, page_1]

# update tables and graphs according to user inputs
@app.callback(
    [
    Output('no-results-alert', 'is_open'),
    Output('no-results-alert', 'children'),
    Output('total_no_rentals', 'children'),
    Output('selected_rentals', 'children'),
    Output('avg-dist-first', 'children'),
    Output('avg-dist-second', 'children'),
    Output('avg-dist-third', 'children'),
    Output('table', 'data'),
    Output('map', 'srcDoc'),
    Output('type-price-rating', 'figure'),
    Output('yelp-table', 'data'),
    Output('price-histogram', 'figure'),
    Output('price-type', 'figure'),
    Output('crimes-by-hour', 'figure'),
    Output('crimes-by-day', 'figure')
    ],

    [Input('generate_button', 'n_clicks')],

    state = [
        State('price_range', 'value'),
        State('zipcodes', 'value'),
        State('rental_types', 'value'),
        State('laundry', 'value'),
        State('parking', 'value'),
        State('pets', 'value'),
        State('facilities', 'value'),
        State('facilities2', 'value'),
        State('facilities3', 'value')
        ]
)

def update_results(n_clicks, price_range, zipcodes, rental_types, laundry, parking, pets, first, second, third):
    
    if n_clicks is None:
        raise PreventUpdate

    filtered_df = filter_rentals(
        price_range, 
        zipcodes, 
        rental_types, 
        laundry, 
        parking, 
        pets,
        df = rental_df
    )

    n_rentals, _ = filtered_df.shape
    if n_rentals == 0:
        return [
            True, 'Oops! There are no rentals with the selected features. Please select other options and try again',
            '{:,.0f}'.format(df.shape[0]), '0', 
            '', '', '',
            filtered_df.to_dict('records'), 
            open('./maps/mymap.html', 'r').read(),
            dash.no_update, yelp_data.drop_duplicates(subset = 'restaurant name').to_dict('records'),
            dash.no_update, dash.no_update, dash.no_update, dash.no_update
            ]


    ranks = {first: 1, second: 2, third: 3}

    facilities = facilities_db[facilities_db['facgroup'].isin(ranks.keys())]

    distances_df = compute_distances(
        rentals = filtered_df, 
        facilities = facilities, 
        ranks = ranks
        )

    rentals_rank = get_ordering(distances_df)
    rentals_rank_d = {k:v for v, k in enumerate(rentals_rank)}
    filtered_df['zipcode_order'] = filtered_df['zipcode'].map(rentals_rank_d)
    
    filtered_df = filtered_df.merge(crime_count, on = 'ntaname')
    filtered_df['distance'] = filtered_df.apply(
        lambda x: distance(x['latitude'], x['longitude'], x['lat'], x['lon']), axis = 1) 
    filtered_df = filtered_df.sort_values(by = ['distance', 'count'])
    filtered_df = filtered_df.drop_duplicates(subset = ['name', 'address'], keep = 'first')
    
    filtered_df = filtered_df.sort_values(
        by = ['zipcode_order', 'count', 'price', 'rating'], 
        ascending = [True, True, True, False]
        ).reset_index(drop = True)
    
    cols = ['index_right', 'geometry', 'lat', 'lon', 'distance', 'count', 'zipcode_order']
    filtered_df = pd.DataFrame(filtered_df.drop(columns = cols))
    
    current_time = datetime.datetime.now().date()
    path = './maps/' + str(current_time) + '_' + rentals_rank[0] + '.html'
    
    if not os.path.isfile(path):
        save_map(
            filtered_df,
            distances_df,
            best_zipcode = rentals_rank[0]
        )
    
    # --- plots ---
    # yelp plot
    yelp_data_ = yelp_data[yelp_data['Zipcode'] == rentals_rank[0]].sort_values(by = 'rating', ascending = False)
    top_food_types = yelp_data_['food type'].value_counts(normalize = True)[:15].index.to_list()
    type_price_rating = yelp_data_[yelp_data_['food type'].isin(top_food_types)]
    type_price_rating = (
        type_price_rating
        .groupby(
            ['food type', 'price level'], 
            as_index = False)[['num_rating', 'rating']]
        .agg('mean')
    )

    colors_d = {'$':'#ade8f4', '$$':'#48cae4', '$$$':'#0096c7', '$$$$':'#03045e'}
    
    fig5 = px.scatter(
        type_price_rating, 
        x = "food type", 
        y = "rating",
        size = "num_rating", 
        color = "price level",
        size_max = 40,
        hover_data = {'rating': ':.2f', 'num_rating': ':,.0f'},
        color_discrete_map = colors_d
    )

    fig5.update_xaxes(tickangle = 45)

    fig5.update_layout(
        showlegend = False,
        xaxis_title = 'Food Type (top 15)',
        yaxis_title = 'Average Rating',
        height = 400,
        margin = dict(l = 10, r = 10, t = 50, b = 10)
    )

    # rental prices
    nta = str(filtered_df['ntaname'][0])
    prices_data = rental_df[rental_df['ntaname'] == nta]
    colors = ['#4cc9f0', '#4361ee', '#3a0ca3', '#560bad', '#7209b7', '#f72585']
    
    fig3 = px.histogram(
        prices_data, 
        x = 'price',
        nbins = 15,
        title = 'Distribution of Prices',
        color_discrete_sequence = [colors[-1]],
        labels = {'price':'$','count':'no. of rentals'},
        height = 300
        )
    
    fig3.update_layout(
        yaxis_title = "No. of Rentals",
        xaxis_title = 'Price (USD Dollars)',
        margin = dict(l = 20, r = 20, t = 50, b = 20),
        showlegend = False, 
        title_x = 0.5,
        height = 300
        )
        
    fig4 = px.box(
        prices_data, 
        x = 'type', 
        y = 'price')

    fig4.update_layout(
        title_text = 'Distribution of Prices by Rental Type in ' + nta,
        yaxis_title = 'Price (USD Dollars)',
        xaxis_title = 'Type of Rental',
        height = 300
        )

    # crime rates by hour
    nta_crimes = crime_geom[crime_geom['ntaname'] == nta]
    nta_crimes_count = (
        nta_crimes
        .groupby(
            [nta_crimes['datetime'].dt.hour, 'law_cat_cd'], 
            as_index = False)
        .size()
        )
    felony = nta_crimes_count[nta_crimes_count['law_cat_cd'] == 'FELONY']
    misdemeanor = nta_crimes_count[nta_crimes_count['law_cat_cd'] == 'MISDEMEANOR']
    violation = nta_crimes_count[nta_crimes_count['law_cat_cd'] == 'VIOLATION']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = felony['datetime'], 
        y = felony['size'], 
        name = 'Felony',
        marker_color = '#4361ee'
    ))

    fig.add_trace(go.Bar(
        x = misdemeanor['datetime'], 
        y = misdemeanor['size'], 
        name = 'Misdemeanor',
        marker_color = '#480ca8'
    ))

    fig.add_trace(go.Bar(
        x = violation['datetime'], 
        y = violation['size'], 
        name = 'Violation',
        marker_color = '#f72585'
    ))

    fig.update_layout(
        title = nta,
        xaxis_title = 'Hour',
        yaxis_title = 'Number of Crimes',
        height = 305,
        margin = dict(l = 20, r = 20, t = 50, b = 20),
        legend_x = 0,
        legend_y = 1
        )

    # crime rates by day
    nta_crimes_count = (
        nta_crimes
        .groupby(
            [nta_crimes['datetime'].dt.day, 'law_cat_cd'], 
            as_index = False)
        .size()
        )

    felony = nta_crimes_count[nta_crimes_count['law_cat_cd'] == 'FELONY']
    misdemeanor = nta_crimes_count[nta_crimes_count['law_cat_cd'] == 'MISDEMEANOR']
    violation = nta_crimes_count[nta_crimes_count['law_cat_cd'] == 'VIOLATION']

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x = felony['datetime'], 
        y = felony['size'], 
        name = 'Felony',
        line = dict(color = '#4361ee', width = 3)
    ))

    fig2.add_trace(go.Scatter(
        x = misdemeanor['datetime'], 
        y = misdemeanor['size'], 
        name = 'Misdemeanor',
        line = dict(color = '#480ca8', width = 3, dash = 'dash')
    ))

    fig2.add_trace(go.Scatter(
        x = violation['datetime'], 
        y = violation['size'], 
        name = 'Violation',
        line = dict(color = '#f72585', width = 3, dash = 'dashdot')
    ))

    fig2.update_layout(
        title = nta,
        xaxis_title = 'Day',
        yaxis_title = 'Number of Crimes',
        height = 305,
        margin = dict(l = 20, r = 20, t = 50, b = 20),
        showlegend = False
        # legend = dict(
        #     orientation = 'h',
        #     yanchor = "bottom",
        #     y = 1.02,
        #     xanchor = "right",
        #     x = 1)
        )

    # distances cards data
    template = '{}:\n{:.2f} mi'
    first_d = distances_df[distances_df['facgroup'] == first].distance.mean()
    second_d = distances_df[distances_df['facgroup'] == second].distance.mean()
    third_d = distances_df[distances_df['facgroup'] == third].distance.mean()

    return [
        False, '',
        '{:,.0f}'.format(df.shape[0]), 
        '{:,.0f}'.format(filtered_df.shape[0]),
        template.format(first, first_d),
        template.format(second, second_d),
        template.format(third, third_d),
        filtered_df.to_dict('records'), 
        open(path, 'r').read(),
        fig5,
        yelp_data_.drop_duplicates(subset = ['restaurant name']).to_dict('records'),
        fig3, 
        fig4,
        fig, 
        fig2
    ]

if __name__ == "__main__":
    app.run_server(debug = False)