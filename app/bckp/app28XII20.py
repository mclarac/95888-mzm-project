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

import flask
import os
import datetime

# read the data
facilities_db = pd.read_csv('../cleaned-data/manhattan-surroundings_cleaned.csv', dtype = {'zipcode':str})
rental_df = pd.read_csv('../cleaned-data/manhattan-rental_cleaned.csv', dtype = {'zipcode':str})
cols = ['zipcode', 'name', 'address', 'contact', 'rating', 'type', 'price']
df = rental_df[cols].sort_values(by = ['price', 'rating'], ascending = [True, False])

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
                        src = 'https://www.flaticon.com/svg/static/icons/svg/481/481270.svg',
                        className = 'icons_nav'),
                        '  ', "Top Recommendations"
                        ],
                        href = "/page-1", id = "page-1")
                        ]),
                
            dbc.NavItem([
                dbc.NavLink([
                    html.Img(
                        src = "https://www.flaticon.com/svg/static/icons/svg/1818/1818913.svg",
                        className = 'icons_nav'),
                        ' ' , "Report"
                        ], 
                        href = "/page-2", id = "page-2")
                        ],
                        className = 'mr-5 ml-3 mx-auto center_nav')
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
    
    html.Br(),

    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4('Location of top recommendation'),
                    html.Iframe(
                        id = 'map',
                        style = {'border': 'none', 'width': '100%', 'height': 400},
                        srcDoc = open('./maps/mymap.html', 'r').read()
                    )]
                )
            ),
            width = {'size': 12}
        )
    ]),
    
    # table with rental details
    dbc.Row([
        dbc.Col(
            dbc.Card(
                dbc.CardBody(
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
                    ))),
                width = {'size': 12}
        )
    ])
])

# Join up pages
page_1 = html.Div([
    dbc.Row([
        dbc.Col(user_opts, width = {'size': 4, 'offset': 0}),
        dbc.Col(recommendations, width = {'size': 8})
    # dbc.Row(dbc.Col(bw_graphics, width={'size': 12}))
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
    [Output("error_log", "children"), Output("url","pathname")],
    [Input("login_button", 'n_clicks')],
    [State("username", "value"), State("password", "value")]
    )
def index_validation(n_clicks, user, password):

    if (user is None) or (password is None) :
        return '', dash.no_update

    elif user in users.keys():
        if users[user] == password:
            return 'Correct',"/page-1"
        else:
            return 'Contraseña Incorrecta', dash.no_update
    else: 
        return 'Usuario no existe', dash.no_update

# navigation in the dashboard
@app.callback(
    Output("page-content", "children"), 
    Input("url", "pathname")
    )
def render_page_content(pathname):
    if (pathname in ["/", "/index"]):
        return index
    elif (pathname == "/page-1"):
        return [side_nav, page_1]
    elif (pathname == "/page-2"):
        return [side_nav, page_2]

@app.callback(
    [Output('total_no_rentals', 'children'),
     Output('selected_rentals', 'children'),
     Output('table', 'data'),
     Output('map', 'srcDoc')],
    [Input('price_range', 'value'),
     Input('zipcodes', 'value'),
     Input('rental_types', 'value'),
     Input('laundry', 'value'),
     Input('parking', 'value'),
     Input('pets', 'value'),
     Input('facilities', 'value'),
     Input('facilities2', 'value'),
     Input('facilities3', 'value')]
)

def update_results(price_range, zipcodes, rental_types, laundry, parking, pets, first, second, third):
    
    filtered_df = filter_rentals(
        price_range, 
        zipcodes, 
        rental_types, 
        laundry, 
        parking, 
        pets,
        df = rental_df
    )

    ranks = {first: 1, second: 2, third: 3}

    facilities = facilities_db[facilities_db['facgroup'].isin(ranks.keys())]

    distances_df = compute_distances(
        rentals = filtered_df, 
        facilities = facilities, 
        ranks = ranks
        )

    rentals_rank = get_ordering(distances_df)

    filtered_df.zipcode = pd.Categorical(
        values = filtered_df.zipcode, 
        ordered = True, 
        categories = set(rentals_rank)
        )

    filtered_df = filtered_df.sort_values(
        by = ['zipcode', 'price', 'rating'], 
        ascending = [True, True, False]
        )

    current_time = datetime.datetime.now().date()
    
    path = './maps/' + str(current_time) + '_' + rentals_rank[0] + '.html'
    
    if not os.path.isfile(path):
        save_map(
            filtered_df,
            distances_df,
            best_zipcode = rentals_rank[0]
        )

    return['{:,.0f}'.format(df.shape[0]), '{:,.0f}'.format(filtered_df.shape[0]),
           filtered_df.to_dict('records'), open(path, 'r').read()]

if __name__ == "__main__":
    app.run_server(debug = False)