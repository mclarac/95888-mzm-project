# -*- coding: utf-8 -*-
"""
Created on Wed Nov 18 16:23:18 2020
@authors: María Lara C (mlaracue), Mengyao Xu (mengyaox) and Lu Zhang (luzhang3)

This script will download and clean the crime, restaurants and facilities 
data bases by using the NYC Open Data API (Socrata)
"""
import pandas    as pd 
import geopandas as gpd
from sodapy      import Socrata

access_info = {}
with open('./nycopendata-API-key.txt', 'r') as f:
    for line in f:
        line = line.split(':')
        access_info[line[0]] = line[1].strip()

# create the client to make the requests
client = Socrata('data.cityofnewyork.us', 
                 access_info['App Token'],  
                 username = access_info['Key ID'],
                 password = access_info['Key Secret'])

# --- crime data ---
# define the query for crime data only for Manhattan
myquery = "SELECT law_cat_cd, cmplnt_fr_dt, cmplnt_fr_tm, latitude, longitude WHERE boro_nm = 'MANHATTAN' LIMIT 10000"
# make the request of 10,000 records only for Manhattan
crimes_data = client.get("5uac-w243", query = myquery)
# save the results into a data frame
crime_df = pd.DataFrame.from_records(crimes_data)

# data cleaning
# first of all, we'll join the date column and the time column together. For that, we'll:
# 1. get rid of the substring *T00:00:00.000* in the date column (`cmplnt_fr_dt`)
# 2. append the time column (`cmplnt_fr_tm`)
# 3. converte the column to datetime to extract info like the hour and the day of the week
crime_df['cmplnt_fr_dt'] = crime_df['cmplnt_fr_dt'].str.replace('T00:00:00.000', '')
crime_df['datetime'] = crime_df['cmplnt_fr_dt'] + ' ' + crime_df['cmplnt_fr_tm']
crime_df['datetime'] = pd.to_datetime(crime_df['datetime'])
crime_df.drop(columns = ['cmplnt_fr_dt', 'cmplnt_fr_dt'], inplace = True)

# Given that we only downloaded the first 10,000 records, we have data primarily only for September, 2020. 
# So, we'll keep September records and then analyze the offense trends by day. 
crime_df = crime_df[crime_df['datetime'].dt.to_period('M') == '2020-09']
# change latitude and longitude to float
crime_df['latitude'] = crime_df['latitude'].astype(float)
crime_df['longitude'] = crime_df['longitude'].astype(float)
# now, we need to append the ntaname and the ntacode from the previously downloaded shape file for NYC
nyc_ntas = gpd.read_file('./raw-data/nyc-TNA.geojson', driver = "GeoJSON")
gdf_crime = gpd.GeoDataFrame(crime_df, geometry = gpd.points_from_xy(crime_df.longitude, crime_df.latitude))
crime_geom = gpd.sjoin(left_df = gdf_crime, right_df = nyc_ntas[['geometry', 'ntaname', 'ntacode']], how = 'inner')
crime_geom.drop(columns = ['index_right', 'geometry'], inplace = True)
# save the results into a csv file
crime_geom.to_csv('./cleaned-data/manhattan-crime_cleaned.csv', index = False)

# --- restaurants data ---
# define the query for restaurants data only for Manhattan
myquery = "SELECT restaurantname, businessaddress, postcode, latitude, longitude WHERE borough = 'Manhattan' LIMIT 10000"
# make the request of 10,000 records
restaurants_data = client.get("4dx7-axux", query = myquery)
# save the results into a data frame
restaurants_df = pd.DataFrame.from_records(restaurants_data)

# data cleaning
# change latitude and longitude to float
restaurants_df['latitude'] = restaurants_df['latitude'].astype(float)
restaurants_df['longitude'] = restaurants_df['longitude'].astype(float)
# we need to append the ntacode from the previously downloaded shape file for NYC
gdf_restaurants = gpd.GeoDataFrame(
    restaurants_df, 
    geometry = gpd.points_from_xy(
        restaurants_df.longitude, 
        restaurants_df.latitude)
)
restaurants_geom = gpd.sjoin(
    left_df = gdf_restaurants, 
    right_df = nyc_ntas[['geometry', 'ntacode']], 
    how = 'inner'
)
restaurants_geom.drop(columns = ['geometry', 'index_right'], inplace = True)
# we'll create a new variable called 'facgroup' to be included in the facilities_db that is created below
restaurants_geom['facgroup'] = 'Restaurants'
# now, we change the name of the columns to be consistents with the columns of facilities_db
restaurants_geom.columns = ['facname', 'address', 'zipcode', 'latitude', 'longitude', 'ntacode', 'facgroup']
# save the data into a csv file
restaurants_geom.to_csv('./cleaned-data/manhattan-restaurants_cleaned.csv', index = False)

# --- surroundings data ---
# define the query for surroundings data
myquery = "SELECT facgroup, facname, address, zipcode, nta, latitude, longitude WHERE boro = 'Manhattan'"
surroundings_data = client.get("67g2-p84d", query = myquery)
facilities_db = pd.DataFrame.from_records(surroundings_data)

# data cleaning
# we'll exclude some facilities that we think are not of interest of our users
exclude_facilities = ['Other property', 
                      'Solid waste', 
                      'Justice and corrections', 
                      'Water and wastewater', 
                      'Material supplies and markets',
                      'Telecommunications']

facilities_db['facgroup'] = facilities_db['facgroup'].str.capitalize()
facilities_db['facname'] = facilities_db['facname'].str.title()
facilities_db = facilities_db[~facilities_db['facgroup'].isin(exclude_facilities)]
# change the name of the nta column
facilities_db = facilities_db.rename(columns = {'nta': 'ntacode'})
# combine the two dataframes together
facilities_db = pd.concat([facilities_db, restaurants_geom], axis = 0)
# save the results into a data frame and then into a csv file
facilities_db.to_csv('./cleaned-data/manhattan-surroundings_cleaned.csv', index = False)