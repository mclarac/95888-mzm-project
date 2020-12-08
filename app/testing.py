# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 17:39:31 2020
@author: María Lara Cuervo
"""
import pandas                    as pd
import geopandas                 as gpd

from myfuncs import filter_rentals, compute_distances, get_ordering

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

# helpers
zipcodes_l = sorted(list(rental_df['zipcode'].unique()))
facilities_l = sorted(list(facilities_db['facgroup'].unique()))
rental_types_l = ['Studio', '1 Bedroom', '2 Bedrooms', '3 Bedrooms', '4+ Bedrooms']

# user opts
price_range = [1300, 4500]
zipcodes = ['10001', '10003']
rental_types = ['2 Bedrooms', 'Studio']
laundry = 0
parking = 0
pets = 0
first = 'Health care'
second = 'Transportation'
third = 'Cultural institutions'

rental_df['type'].unique()

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

yelp_data = pd.read_csv('../cleaned-data/yelp-restaurants_cleaned.csv', dtype = {'Zipcode':str})

yelp_data_ = yelp_data[yelp_data['Zipcode'] == rentals_rank[0]]
top_food_types = yelp_data_['food type'].value_counts(normalize = True)[:15].index.to_list()
type_price_rating = yelp_data_[yelp_data_['food type'].isin(top_food_types)]
type_price_rating = (
    type_price_rating
    .groupby(
        ['food type', 'price level'], 
        as_index = False)[['num_rating', 'rating']]
    .agg('mean')
)


