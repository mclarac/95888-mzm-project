# -*- coding: utf-8 -*-
"""
@authors: Maria Lara C (mlaracue), Mengyao Xu (mengyaox) and Lu Zhang (luzhang3)
This module contains the main functions used by app.py
"""
import pandas       as pd
from folium.plugins import MarkerCluster
import folium

def filter_rentals(price_range, zipcodes, rental_types, laundry, parking, pets, df):
    '''
    Filters the rentals dataframe based on the user's choices
    '''
    
    min_price, max_price = price_range

    mask = (
        (df['price'] >= min_price) & (df['price'] <= max_price) &
        (df['laundry_code'] == laundry) &
        (df['parking_code'] == parking) &
        (df['pet_code'] == pets)
        )
    
    df = df[mask]
    
    if isinstance(zipcodes, str):
        df = df[df['zipcode'] == zipcodes]
    else:
        df = df[df['zipcode'].isin(zipcodes)]
    
    if isinstance(rental_types, str):
        df = df[df['type'] == rental_types]
    else:
        df = df[df['type'].isin(rental_types)]
    
    return df.reset_index(drop = True)
    
def distance(lat1, lon1, lat2, lon2):
    from math import sin, cos, sqrt, atan2, radians
    '''
    This function takes two coordinates and returns 
    the distance (in miles) between the two locations

    Parameters:
    ----------
        lat1: float. Latitude of location 1
        lon2: float. Longitude of location 1
        lat2: float. Latitude of location 2
        lon1: float. Longitude of location 2
    
    Returns: 
    --------
    distance between two coordinates in miles (float)
    '''
    # approximate radius of earth in km
    R = 6373.0
    
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    d = R * c * 0.621371
    
    return d

def compute_distances(rentals, facilities, ranks, miles = 0.25):
    '''
    This functions computes the distance between all rentals
    and surroundings (or facilities) and keeps only facilities from
    which the distance to the rental (by zipcode) is less than 'miles'
    This function depends on the 'distance' function.

    Parameters:
    ----------
        rentals: pandas dataframe with all rentals with the
        columns zipcode, latitude and longitude
        facilities: pandas dataframe with surroundings (or facilities)
        with the columns latitude, longitude and facgroup
        rank : a dictionary with the ordering of user's preference.
        For example {'Health care': 1, 'Transportation': 2, 'Restaurants': 3}
        miles: the cutoff to define when a facility is close enough to a rental.
        Default is 0.25 (walking distance)
    
    Returns:
    -------
    a dataframe with facilities that are within x miles from each rental
    (defined by the 'miles' param)
    '''
    rentals = rentals.drop_duplicates(subset = ['zipcode'])
    distances_df = pd.DataFrame({})
    zip_codes = []
    left_index = []
    distances = []
    
    for i, row in rentals.iterrows():
        lat1, lon1 = row['latitude'], row['longitude']
        for j, row2 in facilities.iterrows():
            lat2, lon2 = row2['latitude'], row2['longitude']
            d = distance(lat1, lon1, lat2, lon2)
            zip_codes.append(row['zipcode'])
            left_index.append(j)
            distances.append(d)

    distances_df = pd.DataFrame({'zipcode': zip_codes, 'place_index': left_index, 'distance': distances})
    facilities = facilities.rename_axis('place_index').reset_index()
    distances_df = distances_df.merge(right = facilities, on = 'place_index')
    distances_df['rank'] = distances_df['facgroup'].map(ranks)
    
    distances_df = distances_df[distances_df['distance'] <= miles]

    return distances_df

def get_ordering(distances_df):
    '''
    This function computes and index based on user's ranking of
    surroundings (or facilites) and returns an ordering for 
    listings recommendations. The index assigns more relevance 
    to rentals that are closer to the facilities within the 
    top user's preference. Both the number of facilities and 
    the proximity are taken into account. 

    Parameters:
    -----------
        distances_df = pandas dataframe returned by the 
        compute_distances() function
    
    Returns:
    --------
    list type with zipcodes ordering from best to worst
    '''
    n_zipcodes = distances_df.zipcode_x.nunique()
    n_rows, _ = distances_df.shape
    
    # if it's an empty dataframe, it means that we don't 
    # have any properties with user's selected choices
    if n_rows == 0:
        return None
    # if there is only one zipcode, no ordering needed
    elif n_zipcodes == 1:
        return list(distances_df.zipcode_x.unique())
    else:
        pd.options.mode.chained_assignment = None
        
        order = (distances_df
                .groupby(['zipcode_x', 'facgroup', 'rank'], as_index = False)
                .agg({'place_index':'count', 'distance':'mean'})
                )
    
        order['index'] = order['place_index'] / order['distance']
        order = order.sort_values(by = 'facgroup')

        # this function is defined within the get_ordering function because
        # it's the only function that uses it.
        def min_max_t(x):
            '''
            This function takes a pandas series or list
            and returns a re-scaled series from 0 to 100
            '''
            if len(x) == 1:
                return 100
            else:
                return (x - x.min()) / (x.max() - x.min()) * 100

        # the places selected by the user
        top_three_places = list(distances_df.facgroup.unique())
        order_ = pd.DataFrame({})
        for i in top_three_places:
            tmp = order[order['facgroup'] == i]
            tmp['index'] = min_max_t(tmp['index'].values)
            order_ = pd.concat([order_, tmp], axis = 0)

        order_['lambda'] = (4 - order_['rank']) / 3
        order_['index_t'] = order_['index'] * order_['lambda']
        order_ = order_.pivot_table(index = 'zipcode_x', columns = 'facgroup', values = 'index_t').reset_index()
        order_['order'] = order_.sum(axis = 1)
        order_ = order_.sort_values(by = 'order', ascending = False).reset_index(drop = True)
        
        return list(set(order_['zipcode_x']))

def save_map(filtered_df, distances_df, best_zipcode, path = './maps/'):
    '''
    This plots the top recommendation along with all the surrounding places
    that are important for the user and save the map into the app/maps/ folder.
    Every map has a unique identified, as follows:
        YYYY-MM-DD_ZC_FirstSecondThird.htlm
    Where:
        ZC: Zipcode of top recommendation
        First: place ranked as most important in user's selections
        Second: place ranked as second in user's selections
        Third: place ranked as third in user's selections
    '''
    import datetime
    
    all_facilities = set(distances_df['facgroup'])
    
    colors = ['darkpurple', 'lightgreen', 'pink']

    # list of icons taken from https://fontawesome.com/icons
    icons_d = {
        'Adults services': 'user',
        'Camps': 'fire',
        'Child services and welfare': 'child',
        'City agency parking, maintenance, and storage': 'automobile',
        'Cultural institutions': 'building',
        'Day care and pre-kindergarten': 'heart',
        'Health care': 'heartbeat',
        'Higher education': 'university',
        'Historical sites': 'history',
        'Human services': 'user',
        'Libraries': 'book',
        'Offices, training, and testing': 'university',
        'Parks and plazas': 'tree',
        'Schools (k-12)': 'university',
        'Transportation': 'bus',
        'Vocational and proprietary schools': 'university',
        'Youth services': 'heart'
        }

    # generate a dictionary a color and an icon for each facility group
    icons_dict = {}
    for i, f in enumerate(all_facilities):
        try:
            d = {'icon': icons_d[f], 'color': colors[i]}
        except:
            d = {'icon': 'info-sign', 'color': colors[i]}
        icons_dict[f] = d
    
    # the location of top recommendation
    location = filtered_df.loc[0, ['latitude', 'longitude']].to_list()
    # the facilities that are in proximity to top recommendation
    top_place_df = distances_df[distances_df['zipcode_x'] == best_zipcode]
    # since there are many rentals for each zipcode (top recommendation)
    # we remove duplicates to preserve one instance of each facility
    # top_place_df = top_place_df.drop_duplicates(subset = ['facname'])
    
    # generate the map with location of top recommendation
    m = folium.Map(
        location = location,
        tiles = 'Stamen Toner',
        zoom_start = 13
    )
    
    # create a radius circle for top recommendation
    folium.Circle(
        radius = 500,
        location = location,
        popup = best_zipcode,
        color = '#3186cc',
        fill = True,
        fill_color = '#3186cc'
    ).add_to(m)
    
    # now, we create a MarketCluster; i.e. if several facilities are very
    # close to each other, they are clustered to enhance readability
    marker_cluster = MarkerCluster().add_to(m)

    for i, r in top_place_df.iterrows():
        location = (r["latitude"], r["longitude"])
        facgroup = r['facgroup']
        folium.Marker(
            location = location,
            popup = facgroup,
            tooltip = r['facname'],
            icon = folium.Icon(
                color = icons_dict[facgroup]['color'], 
                icon = icons_dict[facgroup]['icon'],
                prefix = 'fa')
        ).add_to(marker_cluster)
    
    # create a timestamp to now when the map was generated
    current_time = datetime.datetime.now().date()
    
    # specify the facilities that are being used in the file name
    top_three = ''.join([x[:4] for x in all_facilities])

    # create the path where the map is going to be saved
    path = path + str(current_time) + '_' + best_zipcode + '-' +  top_three  + '.html'
    # path = path + str(current_time) + '_' + best_zipcode + '.html'
    
    # save the map into an html file
    m.save(path)
    
    return