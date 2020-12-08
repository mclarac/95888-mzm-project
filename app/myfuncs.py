import folium
import pandas       as pd
from folium.plugins import MarkerCluster

def filter_rentals(price_range, zipcodes, rental_types, laundry, parking, pets, df):
    
    min_price, max_price = price_range

    mask = (
        (df['price'] >= min_price) & (df['price'] <= max_price) &
        (df['laundry_code'] == laundry) &
        (df['parking'] == parking) &
        (df['pets'] == pets)
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

    Params:
        lat1: float. Latitude of location 1
        lon2: float. Longitude of location 1
        lat2: float. Latitude of location 2
        lon1: float. Longitude of location 2
    
    returns: distance between two coordinates in miles
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

def compute_distances(rentals, facilities, ranks):
    
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
    
    # d_quantile = distances_df['distance'].quantile(.01)
    distances_df = distances_df[distances_df['distance'] <= 0.25]

    return distances_df

def get_ordering(distances_df):
    
    n_zipcodes = distances_df.zipcode_x.nunique()
    n_listings, _ = distances_df.shape
    
    if n_listings == 0:
        return None
    elif n_zipcodes == 1:
        return list(distances_df.zipcode_x)
    else:
        pd.options.mode.chained_assignment = None
        
        order = (distances_df
                .groupby(['zipcode_x', 'facgroup', 'rank'], as_index = False)
                .agg({'place_index':'count', 'distance':'mean'})
                )
    
        order['index'] = order['place_index'] / order['distance']
        order = order.sort_values(by = 'facgroup')
    
        def min_max_t(x):
            return (x - x.min()) / (x.max() - x.min()) * 100
        
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
        
        return list(order_['zipcode_x'])

def save_map(filtered_df, distances_df, best_zipcode, path = './maps/'):
    
    import datetime
    
    icons_dict = {'Health care': {'icon': 'heartbeat', 'color': 'blue'},
                  'Transportation': {'icon': 'bus', 'color': 'red'},
                  'Cultural institutions': {'icon': 'building', 'color': 'green'}}

    location = filtered_df.loc[0, ['latitude', 'longitude']].to_list()
    
    top_place_df = distances_df[distances_df['zipcode_y'] == best_zipcode]
    
    top_place_df = top_place_df.drop_duplicates(subset = ['facname'])
    
    m = folium.Map(
        location = location,
        tiles = 'Stamen Toner',
        zoom_start = 15
    )
    
    folium.Circle(
        radius = 500,
        location = location,
        popup = best_zipcode,
        color = '#3186cc',
        fill = True,
        fill_color = '#3186cc'
    ).add_to(m)
    
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
        
    current_time = datetime.datetime.now().date()
    
    path = path + str(current_time) + '_' + best_zipcode + '.html'
    
    m.save(path)
    
    return