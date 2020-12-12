# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 19:44:34 2020
@author: María Lara Cuervo
"""

import pandas as pd
import numpy as np
import requests
import json
import time

API_KEY = open('./PlacesAPI-key.txt').readlines()[0]
coordinates = ['40.741068', '-73.981506']
text_input = 'Handcraft Kitchen & Cocktails'
fields = ['formatted_address', 'name', 'price_level', 'rating', 'user_ratings_total' ,'geometry']

url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
def create_url(url, text_input, coordinates, fields, key = API_KEY):
    text_input = text_input.replace(' ', '%20')
    url = url + 'input=' + text_input
    url = url + '&inputtype=textquery&fields=' + ','.join(fields)
    url = url + '&locationbias=circle:2000@' + ','.join(coordinates)
    url = url + '&key=' + key
    return url

myurl = create_url(url, text_input, coordinates, fields, key = API_KEY)  

response = requests.get(myurl)
jj = json.loads(response.text)
results = jj['candidates']

final_data = []
for result in results:
    name = result['name']
    formated_address = result['formatted_address']
    lat = result['geometry']['location']['lat']
    lng = result['geometry']['location']['lng']
    price_level = result['price_level']
    rating = result['rating']
    user_ratings_total = result['user_ratings_total']
    data = [name, formated_address, lat, lng, price_level, rating, user_ratings_total]
    final_data.append(data)
    
data = pd.DataFrame.from_dict(result)
