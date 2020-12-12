# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 15:14:16 2020
@author: lu zhang

This code contains two parts:
    Part I: Scarp restaurants from Yelp 
            we have a base data file for yelp data, if user choose to refresh the data
            we will only update the exsiting file.
            
    Part II: Clean raw data scarped from Yelp
            Our Yelp data will containt the following attributes:
            'names', 'ratings', 'num_rating', 'locations', 'price level',
            'food types', 'Zipcode', 'Phone_Numer', 'Outdoor Seating',
            'Sit down Dinning', 'Outdoor seating', 'Delivery', 'Curbside pickup'

"""


from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time  

# =============================================================================
#  Part I: Scarp restaurants from Yelp 
# =============================================================================


# Define attributes to scarp from Yelp 
class business_details:
    def __init__(self, names, ratings, num_ratings, price_types, locations, hour, services, phone):
        self.names = names
        self.ratings = ratings
        self.num_ratings = num_ratings
        self.price_types = price_types
        self.locations = locations
        self.hour = hour
        self.services = services
        self.phone = phone

# Scarp Function    
def get_restaurants_details(page_link):
    
    Next_page = True
    driver.get(page_link)
    while Next_page:
        # get list of buesiness for the current web page
        ls_business = driver.find_elements_by_xpath('.//div[@class=" container__09f24__21w3G hoverable__09f24__2nTf3 margin-t3__09f24__5bM2Z margin-b3__09f24__1DQ9x padding-t3__09f24__-R_5x padding-r3__09f24__1pBFG padding-b3__09f24__1vW6j padding-l3__09f24__1yCJf border--top__09f24__1H_WE border--right__09f24__28idl border--bottom__09f24__2FjZW border--left__09f24__33iol border-color--default__09f24__R1nRO"]')
        
        # Scarp the current web page
        for i in range(len(ls_business)):#
            the_business = business_details('','','','','','','', '')
            business_click = ls_business[i].find_element_by_xpath('.//h4[@class=" heading--h4__09f24__2ijYq alternate__09f24__39r7c"]')
            business_link =business_click.find_element_by_tag_name('a').get_attribute('href')
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(business_link) #
            time.sleep(3)
            # business info
            try:
                left_side = driver.find_element_by_xpath('.//div[@class="lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT arrange-unit-grid-column--8__373c0__2dUx_ padding-r2__373c0__28zpp border-color--default__373c0__3-ifU"]')
                photo_header_content = driver.find_element_by_xpath('.//div[@class="lemon--div__373c0__1mboc photo-header-content__373c0__j8x16 padding-r2__373c0__28zpp border-color--default__373c0__3-ifU"]')
            except NoSuchElementException:
                print('listing not found')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            # business name
            try:
                name = photo_header_content.find_element_by_xpath('./div/div//div/h1')
                if name.text in existing_records:
                    #print('existing record')
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    continue
                the_business.names = name.text
            except NoSuchElementException:
                print('listing not available')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                continue
            
            # business rating
            try:
                rating = photo_header_content.find_element_by_xpath('./div/div/div/div/span[@class="lemon--span__373c0__3997G display--inline__373c0__3JqBP border-color--default__373c0__3-ifU"]')
                the_business.ratings = rating.find_element_by_tag_name('div').get_attribute('aria-label')
            except NoSuchElementException:
                the_business.ratings  = 'N/A'
                
            # number of business ratings
            try:
                num_rating = photo_header_content.find_element_by_xpath('./div/div/div/div[@class="lemon--div__373c0__1mboc arrange-unit__373c0__o3tjT border-color--default__373c0__3-ifU nowrap__373c0__35McF"]')
                the_business.num_ratings = num_rating.text
            except NoSuchElementException:
                the_business.num_ratings = 'N/A'
                
            # Business price level
            price_types = photo_header_content.find_elements_by_xpath('./div/div/span')
            price_type_str = ''
            for j in range(len(price_types)):
                price_type_str += (price_types[j].text) + ', '
            the_business.price_types = price_type_str
            
            #Business location
            try:
                location = driver.find_element_by_xpath('.//address[@class="lemon--address__373c0__2sPac"]')
                the_business.locations = location.text
            except NoSuchElementException:
                the_business.locations = 'N/A'
            
            # Business hours
            try:
                hour = driver.find_element_by_xpath('.//table')
                the_business.hour = hour.text
            except NoSuchElementException:
                the_business.hour = 'N/A'
            
            # Business covid 19 Services
            services_avaliable = []
            #covid_updates = driver.find_elements_by_xpath('.//section[@class="lemon--section__373c0__fNwDM margin-t4__373c0__1TRkQ padding-t4__373c0__3hVZ3 border--top__373c0__3gXLy border-color--default__373c0__3-ifU"]')[0].find_elements_by_xpath('./div') # the first section
             # the first section
            try:
                covid_updates = left_side.find_element_by_xpath('./section').find_elements_by_xpath('./div')
                update_service= covid_updates[len(covid_updates)-1].find_element_by_xpath('./div')
                list_update_service = update_service.find_elements_by_xpath('./div/div')
                if len(list_update_service) == 1:
                        try:
                            service_status = update_service.find_element_by_xpath('./div/div').find_element_by_xpath('./div/span').get_attribute('class')
                            service_type = update_service.find_element_by_xpath('./div/div').text
                            services_avaliable.append([service_type,service_status])
                        except NoSuchElementException:
                            services_avaliable.append(update_service.text)
                else:    
                    for i in range(len(list_update_service)):
                        try:
                            service_status = list_update_service[i].find_element_by_xpath('./div/span').get_attribute('class')
                            service_type = list_update_service[i].text
                            services_avaliable.append([service_type, service_status])
                        except NoSuchElementException:
                            services_avaliable.append('N/A')
            except NoSuchElementException:
                services_avaliable.append('N/A')
                
            the_business.services = services_avaliable
            
            # Business phone number
            try:
                sticky_side = driver.find_element_by_xpath('.//div[@class="lemon--div__373c0__1mboc stickySidebar__373c0__3PY1o border-color--default__373c0__3-ifU"]')
                the_business.phone = sticky_side.text
            except NoSuchElementException:
                the_business.phone = 'N/A'
               
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            all_restaurants.append(the_business)
            
        #Continue to next page
        try:
            next_page = driver.find_element_by_xpath('.//a[@class=" link__09f24__1kwXV next-link navigation-button__09f24__3F7Pt link-color--inherit__09f24__3PYlA link-size--inherit__09f24__2Uj95"]')
            next_page_link = next_page.get_attribute('href')
            driver.get(next_page_link)
        except NoSuchElementException:
            print('No more Next page for the current distinct')
            Next_page = False


# read exsiting yelp raw data
raw_data = pd.read_csv(r'../raw-data/yelp_rest_raw.csv')

existing_records = raw_data['names'].tolist()

# Define Lower Manhattan Disticts
districts = ['East_Village', 'Financial_District', 
             'Greenwich_Village' , 'NoHo', 'West_Village',
             'Lower_East_Side', 'SoHo', 
             'Nolita', 'Little_Italy', 
             'Chinatown', 'Civic_Center', 'Battery_Park', 
             'Alphabet_City', 'Meatpacking_District', 'South_Village',
             'Two_Bridges', 'TriBeCa']

# Start Scarp Yelp website, get updated restaurants
driver = webdriver.Chrome()   
driver.maximize_window()
whole_link =''
front_link = 'https://www.yelp.com/search?find_desc=Restaurants&find_loc=Manhattan%2C%20NY&l=p%3ANY%3ANew_York%3AManhattan%3A' 
all_restaurants = []  
for i in range(len(districts)):
    whole_link = front_link + districts[i]
    print('current scarping: ' ,districts[i])
    get_restaurants_details(whole_link)

driver.close()

# append updated restaurants to the exsiting data file
for i in all_restaurants:
    new_row = pd.Series([i.names, i.ratings, i.num_ratings, i.price_types, i.locations, i.hour, i.services, i.phone], 
                            index = raw_data.columns)
    raw_data = raw_data.append(new_row, ignore_index = True)
raw_data.to_csv(r'..\raw-data\yelp_rest_raw.csv', index = False)

# Write CSV file for the yelp raw database (first time scarp)
# import csv
# with open('yelp_rest_raw.csv', 'w' ,  newline = '', encoding = 'utf-8-sig') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow([ 'names', 'ratings', 'num_rating','price_types', 'locations', 'hour', 'services','Phone'])
#         for i in all_restaurants:
#             writer.writerow([i.names, i.ratings, i.num_ratings, i.price_types, i.locations, i.hour, i.services, i.phone])

    
# =============================================================================
# Part II: Clean raw data scarped from Yelp
# =============================================================================

# read exsiting file
lower_manhattan_rest = pd.read_csv(r'..\raw-data\yelp_rest_raw.csv')
# ['names', 'ratings', 'num_rating', 'price_types', 'locations', 'hour', 'services', 'Phone']

#1. remove duplicates
lower_manhattan_rest = lower_manhattan_rest.drop_duplicates()


#2. remove bad records: 
# NA business names
lower_manhattan_rest[lower_manhattan_rest.names.isnull()]
lower_manhattan_rest_clean = lower_manhattan_rest.dropna(subset = ['names'])


# bad records for covid-19
lower_manhattan_rest_clean = lower_manhattan_rest_clean[~lower_manhattan_rest_clean['services'].str.contains('directions')]


# 3. clean ratings and reviews
lower_manhattan_rest_clean['ratings'] = lower_manhattan_rest_clean['ratings'].str.replace(' star rating', '')
lower_manhattan_rest_clean['num_rating'] = lower_manhattan_rest_clean['num_rating'].str.replace(r' reviews|review', '')
lower_manhattan_rest_clean['num_rating'] =  lower_manhattan_rest_clean['num_rating'].fillna(0)

# 4. clean price_types
lower_manhattan_rest_clean['price level'] =lower_manhattan_rest_clean['price_types'].str.extract('(\$+)').fillna('')
lower_manhattan_rest_clean['food types'] = lower_manhattan_rest_clean['price_types'].str.replace('(Claimed, )|(Unclaimed, )', '').str.replace('Loading interface..., ', '').str.replace('Restaurants', '')
lower_manhattan_rest_clean['food types'] = lower_manhattan_rest_clean['food types'].str.replace('(\$+), ', '').str[:-2].str.replace(r'^(, )?|^(,)', '')

#bad record for  price and type
lower_manhattan_rest_clean = lower_manhattan_rest_clean[~lower_manhattan_rest_clean['food types'].str.contains('Clothing')]
lower_manhattan_rest_clean = lower_manhattan_rest_clean.drop('price_types', axis =1)


# 5. locations need strip \n? No, as display

# 6. extract zip code
lower_manhattan_rest_clean['Zipcode'] = lower_manhattan_rest_clean['locations'].str.extract(r'(1[0-9]{4})')
lower_manhattan_rest_clean = lower_manhattan_rest_clean.dropna(subset = ['Zipcode'])

# 7.no need for business hour
#lower_manhattan_rest_clean['hour'] =lower_manhattan_rest_clean['hour'].fillna('')
#lower_manhattan_rest_clean['hour'] = lower_manhattan_rest_clean['hour'].str.replace('Closed now\n', '')
lower_manhattan_rest_clean = lower_manhattan_rest_clean.drop('hour', axis =1)

# 8.Phone
phone_pattern = r'\([0-9]{3}\) [0-9]{3}-[0-9]{4}'
lower_manhattan_rest_clean['Phone_Numer'] = lower_manhattan_rest_clean['Phone'].str.extract(r'(\([0-9]{3}\) [0-9]{3}-[0-9]{4})')
lower_manhattan_rest_clean = lower_manhattan_rest_clean.drop('Phone', axis =1)


# 9. Covid updates
lower_manhattan_rest_clean['services'] = lower_manhattan_rest_clean.services.str.replace('icon--24-checkmark-v2 css-yyirv3', 'YES').str.replace('icon--24-close-v2 css-p5yz4n', 'NO')
lower_manhattan_rest_clean['services'] = lower_manhattan_rest_clean['services'].str.replace(r'\[.*\'N/A\',*\]', '')
lower_manhattan_rest_clean['services'] = lower_manhattan_rest_clean['services'].str.replace(r'\[\'?\'?\]', '')
lower_manhattan_rest_clean['covid_updates'] = [line[2: len(line)-2].replace("'","").split('], [') for line in lower_manhattan_rest_clean['services']]

#Service Features including: take out, Sit down Dinning, Outdoor seating, Delivery, Curbside pickup
lower_manhattan_rest_clean['Outdoor Seating'] = ['Yes' if  'Outdoor seating, YES' in line else 'No' if 'Outdoor seating, NO' in line else '' for line in lower_manhattan_rest_clean['covid_updates']]
lower_manhattan_rest_clean['Sit down Dinning'] = ['Yes' if  'Sit-down dining, YES' in line else 'No' if 'Sit-down dining, NO' in line else '' for line in lower_manhattan_rest_clean['covid_updates']]
lower_manhattan_rest_clean['Outdoor seating'] = ['Yes' if  'Outdoor seating, YES' in line else 'No' if 'Outdoor seating, NO' in line else '' for line in lower_manhattan_rest_clean['covid_updates']]
lower_manhattan_rest_clean['Delivery'] = ['Yes' if  'Delivery, YES' in line else 'No' if 'Delivery, NO' in line else '' for line in lower_manhattan_rest_clean['covid_updates']]
lower_manhattan_rest_clean['Curbside pickup'] = ['Yes' if  'Curbside pickup, YES' in line else 'No' if 'Curbside pickup, NO' in line else '' for line in lower_manhattan_rest_clean['covid_updates']]

# Drop unused columns
lower_manhattan_rest_clean = lower_manhattan_rest_clean.drop('covid_updates', axis =1)
lower_manhattan_rest_clean = lower_manhattan_rest_clean.drop('services', axis =1)

# save the cleaned data for recommendation algorithm to use
lower_manhattan_rest_clean.to_csv(r'..\cleaned-data\yelp-restaurants_cleaned.csv', index = False)
