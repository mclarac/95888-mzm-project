# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 18:52:53 2020
@author: María Lara Cuervo
"""
import folium
from folium.plugins import MarkerCluster

icons_dict = {'Health care': {'icon': 'heartbeat', 'color': 'blue'},
              'Transportation': {'icon': 'bus', 'color': 'red'},
              'Cultural institutions': {'icon': 'building', 'color': 'green'}}

best_zipcode = '10002'

location = filtered_df.loc[0, ['latitude', 'longitude']].to_list()

top_place_df = distances_df[distances_df['zip_codes'] == best_zipcode]

from myfuncs import save_map

save_map(filtered_df, distances_df, best_zipcode)
