# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 21:54:45 2020
@authors: María Lara C (mlaracue), Mengyao Xu (mengyaox) and Lu Zhang (luzhang3)

This code contains two parts:
    Part I:
        Scrape rental listing data from apartment.com
        we have a base data file of previously scraped/cached rental listing data. 
        if user chooses to refresh rental listing data, this script will 
        only scrape new listings and update the existing file.
    
    Part II:
        Clean the merged raw data of newly scraped and existing data. 
        our rental data will contain the following attributes :
        'name', 'address','zipcode', 'contact', 'rating', 'review count', 'laundry_code',
        'parking_code', 'pet_code', 'pet', 'parking', '2 Bedrooms', '3 Bedrooms',
        'Studio', '4 Bedrooms', '1 Bedrooms', '6 Bedrooms', '5 Bedrooms'

Imported by: app.py
"""

import selenium
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time, os

##predefined zipcodes for lower manhattan
zips = [10128,10001,10002,10003,10004,10005,10006,10007,10009,
        10010,10011,10012,10013,10014,10016,10017,10018,10019,
        10020,10021,10022,10279,10280,10024,10025,10029,10031,
        10034,10036,10038,10168,10041,10169,11201,10305,11216, 
        11106,11373,11377,11378]
print(zips) 

##TODO:read previously scraped raw data
old_df = pd.read_csv(r'..\raw-data\previous scraped data.csv')
old_list = list(set([i.lower() for i in old_df['name'].tolist()]))
####TODO: scrape rental listing data from apartment.com
##initiating chrome browser 
driver = webdriver.Chrome('chromedriver.exe') 
driver.maximize_window()
##navigate to search page
driver.get('https://www.apartments.com/new-york-ny/')

##initiate empty df to store newly scraped data
new_df = pd.DataFrame(columns = ['name', 'address', 'rating','review count', 'rent','pet', 'parking','laundry','contact'])
for z in range(len(zips)):
    # print('index: ', z)
    print('----Rental Data Refresh '"{:.1%}".format(z/len(zips)) + '----')
    page = 0 
    input_box = driver.find_element_by_id('searchBarLookup')
    input_box.send_keys(zips[z])
    input_box.send_keys(Keys.ENTER)        
    driver.execute_script("return document.readyState")
    while page < 1:
        driver.execute_script("return document.readyState")
        result_list_container = driver.find_element_by_id('placardContainer').find_element_by_xpath('./ul')
        result_list = result_list_container.find_elements_by_xpath('./li')
        # print('page: ', page)
        for i in range(len(result_list)-1):
            driver.execute_script("return document.readyState")
            # print('listing: ', i)
            result_list_container = driver.find_element_by_id('placardContainer').find_element_by_xpath('./ul')
            result_list = result_list_container.find_elements_by_xpath('./li')
            
            result = result_list[i]
            driver.execute_script("arguments[0].scrollIntoView();", result)        
            new_url = result.find_elements_by_tag_name('article')[0].get_attribute('data-url')
            if new_url == None: 
                continue
            ##open listing page on another tab
            driver.execute_script("window.open();")
            driver.switch_to.window(driver.window_handles[-1])
            driver.get(new_url)
            wait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "propertyName")))
            
            new_row = []
            
            ##scrape page
            ##scrape property name, if fail, skip to next listing
            try:
                name = driver.find_element_by_class_name('propertyName').text
                if name.lower() in old_list:
                    # print('exisitng listing')
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                else:
                    pass
                    # print('new listing')
                new_row.append(name)
            except:
                # print('listing unavailable')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            ##scrape address, if fails, skip to next listing 
            try:
                address = driver.find_element_by_class_name('propertyAddress').text
                new_row.append(address)
            except:
                # print('address invalid')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            ##scrape rating and number of reviews
            try:
                rating = float(driver.find_element_by_css_selector('.rating.hasReviews').find_element_by_xpath('./span').get_attribute('content'))
                review_count = driver.find_element_by_class_name('reviewCount').text
            except NoSuchElementException:
                rating = 0
                review_count = 0
            new_row.append(rating)
            new_row.append(review_count)
            
            ##scrape floor plans + rent
            rent_types = driver.find_element_by_class_name('rentalInfoTextContainer').find_elements_by_class_name('rentRollup')
            rent_infos = []
            for r in rent_types:
                rent_info = r.text
                rent_infos.append(rent_info)
            new_row.append(rent_infos)
            
            ##scrape amenities
            amenity_sections = driver.find_element_by_id('amenitiesSection')

            ##scrape pet policy
            try:
                pet_info = amenity_sections.find_element_by_css_selector('.specList.petPolicy.js-spec.shuffle-item.filtered').text
            except:
                try:
                    pet_info = amenity_sections.find_element_by_xpath('.//*[contains(text(),"Pets")]').text
                except NoSuchElementException:
                    pet_info = 'No Pets'
            new_row.append(pet_info)
                    
            ##scrape parking policy
            try:
                parking_info = amenity_sections.find_element_by_css_selector('.specList.parking.js-spec.shuffle-item.filtered').text
            except:
                try:
                    parking_info = amenity_sections.find_element_by_xpath('.//*[contains(text(),"Parking ")]').text
                except NoSuchElementException:
                    parking_info = 'No Parking'
            new_row.append(parking_info)
            
            ##scrape laundry info
            try:
                laundry_info = amenity_sections.find_element_by_xpath('.//*[contains(text(),"Washer/Dryer")]').text
            except NoSuchElementException:
                try:
                    laundry_info = amenity_sections.find_element_by_xpath('.//*[contains(text(),"Laundry")]').text
                except:
                    laundry_info = 'No Laundry'
            new_row.append(laundry_info)
    
            ##scrape property contact info
            contact = driver.find_element_by_class_name('contactPhone').text
            if contact == None or contact == '' :
                try:
                    contact = driver.find_element_by_class_name('phoneNumber').text
                except:
                    contact = ''
            new_row.append(contact)
            
            ##append scrpaed info of this listing to the df
            new_df = new_df.append(pd.Series(new_row,index = new_df.columns),ignore_index=True)
            
            #close tab switch to previous tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        
        ##turn page
        try:
            result_list_container = driver.find_element_by_id('placardContainer').find_element_by_xpath('./ul')
            result_list = result_list_container.find_elements_by_xpath('./li')
            result = result_list[-1]
            page_panel = driver.find_element_by_xpath('.//nav[@id = "paging"]')
            next_button = page_panel.find_element_by_xpath('.//a[@class = "next "]')
            next_button.click()
            page += 1
        except:
            # print('Last Page already') 
            break

##remove empty rent info rows in newdf
bad_index =[]
for i, cell in enumerate(new_df['rent']):
    if cell[0] == '':
        bad_index.append(i)
new_df = new_df.loc[~new_df.index.isin(bad_index)]   



##TODO:merge old and new scraped
df = pd.concat([old_df, new_df], ignore_index=True)

##if target folder not exist, create 
if os.path.exists(r'..\raw-data') == False:
    os.mkdir(r'..\raw-data')
##update old data file with newly scraped data
df.to_csv(r'..\raw-data\previous scraped data.csv', index =False)
driver.quit()

####TODO: cleaning scraped data
import numpy  as np
import re

converter = lambda x: x.strip("[]").replace("'","").split(", ")
df = pd.read_csv(r'..\raw-data\previous scraped data.csv', converters = {'rent':converter})
##create a new copy to further process
cleaned_df = df.copy()

##filter out data with rent_info that failed in scraping correctly
bad_index =[]
for i, cell in enumerate(cleaned_df.rent):
    if cell[0] == '':
        bad_index.append(i)
cleaned_df = cleaned_df.loc[~cleaned_df.index.isin(bad_index)]   
   
##parsing each column 
cleaned_df['address'] = cleaned_df['address'].apply(lambda x: x.split(','))
cleaned_df['zipcode'] = cleaned_df['address'].apply(lambda x: re.findall("\d+", x[2])[0] if len(x) == 3 else re.findall("\d+", x[1])[0])

##making sure listings scraped are within the zipcodes predefined
cleaned_df = cleaned_df.loc[cleaned_df['zipcode'].isin ([str(x) for x in zips])]

cleaned_df['address'] = cleaned_df['address'].apply(lambda x: x[0] if len(x) == 3 else np.nan)
cleaned_df['address'] = np.where(cleaned_df['address'].isna(), cleaned_df['name'], cleaned_df['address'])
cleaned_df = cleaned_df.reset_index(drop=True)

def parse_dash_listing(x):
    """this function parses if floor plan has price ranges,
    outputs the max of that range"""
    beds = x[0].split('$')[0].split('–')
    prices = x[0].split('$')[1].split('–')
    if len(beds) != len(prices):
        temp = [beds[1], prices[0]]
    else:
        temp1 = [[beds[x], prices[x]] for x in range(len(beds))]
        temp = [item for sublist in temp1 for item in sublist]
    if re.search('[^0-9 ]+', temp[0]) == None: 
        temp[0] = temp[0] + re.search('[A-Za-z]+', temp[2]).group() 
    listing = [' '.join(temp[(x*2):(x+1)*2]) for x in range(int(len(temp)/2))]
    return listing 

def re_price_person(col,x):
    """this function parses floor plan that states rent/person,
    use floor plan occupancy * rent/person to 
    recalculate rent for the whole floor plan"""
    numbers = x.replace(',', '').replace('$', '')
    numbers = re.findall("\d+", numbers)
    price = str(int(numbers[0]) * int(numbers[-1]))
    col = col.replace('/ Person', '').strip()
    return col, price
##parse rent column
res = {}
for i, listing in enumerate(cleaned_df['rent']):
    # print(i, listing)
    if listing[0].split('$')[0].count('–') > 0:
        listing = parse_dash_listing(listing)
    n_bedrooms = len(listing)
    res_listing = {}
    for j in range(n_bedrooms):    
        col = re.sub('[^a-zA-Z]+[0-9]', '', listing[j])
        col = col.replace(' / Unit', '') 
        col = col.replace(r'+','')
        col = col.replace('Beds', 'Bedrooms')
        col = col.replace('Bed ', 'Bedrooms')
        col = col.rstrip()
        col = re.sub('(Bedroom$)', 'Bedrooms', col)
        col = re.sub('(Bedroom )','Bedrooms ', col)
        if 'Person' in col: 
            col, price = re_price_person(col,listing[j])
        else:
            if col == ' Bedrooms': 
                continue
            if 'Call for Rent' in col:
                price = 'Call for Rent'
                col = col.replace('Call for Rent', '').rstrip()
            else:
                numbers = listing[j].replace(',', '').replace('$', '')
                numbers = re.findall("\d+", numbers)
                # pending: fix Studio ranges (takes the max )
                if len(numbers) == 2: 
                    price = numbers[1]
                elif len(numbers) == 3:
                    price = numbers[2]
                else: 
                    price = numbers[0]
        res_listing[col] = price
    res[i] = res_listing
rent_col = pd.DataFrame.from_dict(res, orient = 'index').sort_index().fillna(0)

##parse more columns of important features
cleaned_df['pet_code'] = cleaned_df['pet'].apply(lambda x: 0 if 'not' in x.lower() or x == 'No Pets' else 1)
cleaned_df['parking_code'] = cleaned_df['parking'].apply(lambda x: 0 if x == 'No Parking' else 1)

cleaned_df['laundry'] = cleaned_df['laundry'].str.replace('•\n', '')
cleaned_df['review count'] = cleaned_df['review count'].fillna(0)
cleaned_df['review count'] = cleaned_df['review count'].apply(lambda x: list(map(int, re.findall(r'\d+', str(x))))[0])

##parsing laundry info to different levels 
laundry_dict = {'No Laundry': 0, 
                'Laundry Facilities': 1, 
                'Washer/Dryer Hookup' : 2,
                'Washer/Dryer - In Unit': 3, 
                'Washer/Dryer in every home': 3,
                'Washer/Dryer': 2 
               }

cleaned_df['laundry_code'] = cleaned_df['laundry'].map(laundry_dict)
cleaned_df['contact'] = cleaned_df['contact'].fillna('-')

##combine all cleaned/parsed columns
cols = ['name', 'address', 'zipcode', 'contact', 'rating', 'review count','laundry_code', 'parking_code', 'pet_code', 'pet', 'parking']
cleaned_df = cleaned_df[cols].merge(
    right = rent_col, 
    right_index = True, 
    left_index = True
)

##if target folder not exist, create 
if os.path.exists(r'..\cleaned-data') == False:
    os.mkdir(r'..\cleaned-data')
##save cleaned data to working directory for later algorithms 

cleaned_df.to_csv(r'..\cleaned-data\manhattan-rental_cleaned.csv', index=False)
print('----Rental Data Refresh Complete----')
# cleaned_df.to_excel('.\clean_data\cleaned results.xlsx', index=False)
