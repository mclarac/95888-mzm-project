# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 21:43:23 2020

@authors: Maria Lara C (mlaracue), Mengyao Xu (mengyaox) and Lu Zhang (luzhang3)

This script creates and stored the heatmap of crime rates
"""
import pandas            as pd
import geopandas         as gpd
from folium.plugins      import HeatMap
import folium  
import branca

# read the data
crime_geom = pd.read_csv('./cleaned-data/manhattan-crime_cleaned.csv', parse_dates = ['datetime'])
nyc_ntas = gpd.read_file('./cleaned-data/nyc-TNA.geojson', driver = "GeoJSON")

# create a dataframe with crime counts by latitude and longitude
crime_geom["ntaname"] = crime_geom["ntaname"].str.zfill(4)
nta_crime_count = (
    crime_geom.groupby('ntaname')['law_cat_cd']
    .count()
    .reset_index(name = 'crime_count')
)

# max and min for color scheme
min_cn, max_cn = nta_crime_count['crime_count'].quantile([0.01, 0.99]).apply(round, 2)
colormap = branca.colormap.LinearColormap(
    colors = ['white','yellow','orange','red','darkred'],
    vmin = min_cn,
    vmax = max_cn
)

colormap.caption = "Total crimes in Manhattan by NTA"

manhattan_data = nyc_ntas.join(nta_crime_count.set_index("ntaname"), how = "inner", on = "ntaname")

# interactive visualization
m_crime = folium.Map(
    location = [40.745, -74.0060],
    zoom_start = 12,
    tiles = "OpenStreetMap"
)

style_function = lambda x: {
    'fillColor': colormap(x['properties']['crime_count']),
    'color': 'black',
    'weight': 2,
    'fillOpacity':0.5
}

stategeo = folium.GeoJson(
    manhattan_data.to_json(),
    name = 'Manhattan NTA',
    style_function = style_function,
    tooltip = folium.GeoJsonTooltip(
        fields = ['ntaname', 'crime_count'],
        aliases = ['NTA', 'Total crime'],
        localize = True
    )
).add_to(m_crime)

colormap.add_to(m_crime)

m_crime.save('./app/maps/nta_crime_count.html')

m = folium.Map(
    location = [40.783058, -73.971252],
    tiles = 'Stamen Toner',
    zoom_start = 12
)

m.save('./app/maps/NYC-map.html')
