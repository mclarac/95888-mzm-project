# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 16:57:38 2020
@author: María Lara Cuervo
"""

from urllib.request import urlopen
import json

url = "https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NTA_ACS_Demographics/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson"
response = urlopen(url)
demographics_data = response.read().decode("utf-8")
demographics_data = json.loads(demographics_data)

json_object = json.dumps(demographics_data, indent = 4) 

# Writing to sample.json 
with open("./data/nyc-demographics-data.json", "w") as outfile: 
    outfile.write(json_object)