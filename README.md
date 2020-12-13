**95-888D2 Data Focused Python**

*Carnegie Mellon University*

Final project

Group members:

* Mengyao Xu - mengyaox@andrew.cmu.edu
* Lu Zhang - luzhang3@andrew.cmu.edu
* María Lara C - mlaracue@andrew.cmu.edu

# MZM
MZM is a local app that provides recommendations of property rental listings based on users preferences, along with comprehensive reports of neighborhood features. For each property rental listing, our product will give users aggregated information to help them better understand the neighborhood, such as nearby restaurants and neighborhood safety.

## Python Dependencies

At its core, this product depends heavily on the [Dash](https://pypi.org/project/dash/) package. All other requirements can be found in [requirements.txt](https://github.com/mclarac/95888-mzm-project/blob/main/requirements.txt) and [requirements-pip.txt](https://github.com/mclarac/95888-mzm-project/blob/main/requirements-pip.txt). All the dependencies can be installed by opening the Anaconda prompt and navigating to the root folder. Then type:
```
conda install -c conda-forge --yes --file requirements.txt
```

Followed by:
```
pip install -r requirements-pip.txt
```

> Note: installing `geopandas` *can* be a problem; in some computers, it installs smoothly, in others, makes you want to pound your head on the desk. So, if you face some troubles, please please be patient and follow the instructions found in [this](https://geoffboeing.com/2014/09/using-geopandas-windows/) website

## Data Sources
In order for the application to work correctly, the following files need to be stored in the path `./cleaned-data/`:

* `manhattan-surroundings_cleaned.csv`: This data contains information about 35,000+ public and private facilities and program sites that are owned, operated, funded, licensed or certified by a City, State, or Federal agency in the City of New York. It captures facilities that generally help to shape quality of life in the city’s neighborhoods, including schools, day cares, parks, libraries, among others. To know more, please visit [Facilities Database - Shapefile](https://data.cityofnewyork.us/City-Government/Facilities-Database-Shapefile/2fpa-bnsx). This data is retrieved and cleaned using the script `nyc-socrataAPI-requests.py`.
* `manhattan-crime_cleaned.csv`: This data contains every criminal complaint NYC. To know more, please visit [NYPD Complaint Data Current (Year To Date)](https://dev.socrata.com/foundry/data.cityofnewyork.us/5uac-w243). This data is retrieved and cleaned using the script `nyc-socrataAPI-requests.py`.
* `nyc-TNA.geojson`: This data contains boundaries of Neighborhood Tabulation Areas as created by the NYC Department of City Planning using whole census tracts from the 2010 Census as building blocks. These aggregations of census tracts are subsets of New York City's 55 Public Use Microdata Areas (PUMAs). To know more, please visit [Neighborhood Tabulation Areas (NTA)](https://data.cityofnewyork.us/City-Government/Neighborhood-Tabulation-Areas-NTA-/cpf4-rkhq) - Direct download.
* `manhattan-rental_cleaned.csv`: This data contains apartment rental listings in Manhattan with detailed information, such as an address, ratings, the price for each floor plan, pet policies, parking facilities, laundry facilities, etc. It was web scraped (from [Apartments.com](https://www.apartments.com/new-york-ny/)) and cleaned using the script `rental_scrape_clean.py`.
* `yelp-restaurants_cleaned.csv`: This data contains restaurants in Manhattan with detailed information, such as address, ratings, price level, food types, etc. It was web scraped (from [Yelp](https://www.yelp.com)) and cleaned using the script `yelp_scrape_clean.py`.

### NYC Open Data API (Socrata)
The script `nyc-socrataAPI-requests.py` reads and uses an APP token, a key ID, and a key secret. In order to avoid Professor Ostlund and TAs to sign up to NYC Open Data for an app token, the file `nycopendata-API-key.txt` will be provided so they'll be able to run the script without any problems.

### Web Scraping
For the scripts `rental_scrape_clean.py` and `yelp_scrape_clean.py` to work correctly, follow these instructions:

* Step 1: download chrome and install it on your computer if you don’t have one yet. 
* Step 2: check the version of your chrome driver installed at chrome://settings/help, use the first 2 digits for next step. It is recommended if you have version 86 or later.
* Step 3: go to [WebDriver for Chrome](https://chromedriver.chromium.org/downloads), download chromedriver_win32.zip under the correction version release according to step 2. 
* Step 4: open the downloaded zip, and extract chromedriver.exe within to the `.\app\` folder

## Running the app
To run the app go to the Anaconda prompt and navigate to the directory where the app is located (inside the folder `./app/)` - keep in mind that the root folder *must* contain the folders `./app/`, `./raw-data/` and `./cleaned-data/`. Then, just type:
```
python app.py
```

Our product is going to ask you if you want to update the data, which on average takes about four hours, so we do recommend not to do so. Either way, if you want to have the most up-to-date data, please click **YES** in the pop-up window that will appear on your screen.

After the scraping (both of rentals and restaurants) ends, or after you clicked **NO** in the pop-up window, you should see in the prompt the following message:

> Running on http://....

Copy and paste the address into your preferred browser

## Authentication
After you copy the address, you will see a welcome page like the following:![welcome-page](https://github.com/mclarac/95888-mzm-project/blob/main/welcome-page.png?raw=true)

Use these credentials to get access to our product:
* **username**: user1
* **password**: xzbm-VEeLRTM~7)#

Finally, in [this](https://youtu.be/14XD5K5GKOo) link you find the video demonstrating our product being run