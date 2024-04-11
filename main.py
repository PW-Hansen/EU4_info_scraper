import functions_scraping as scrape
from functions import save_info_as_csv
from functions_map import create_province_map, get_neighbors, country_map
from classes import *
import os

#%% TO-DO
# Colors for cultures and religions.
# Technology groups?
# Country flags
# Tribal lands?
# Rivers mapping.
# Adjacencies from straits and the like.

#%% Defines.
DEFINES = {}
DEFINES['MAP_PROVINCES'] = True # Leave at false, there's some issue with pixel colors. 
DEFINES['OUTPUT'] = False # Should always be false if the above is false.
DEFINES['ORIGIN_PATH'] = os.getcwd()
DEFINES['MAIN_PATH'] = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\src'


#%% Actually running stuff.
if __name__ == "__main__":
    path = DEFINES['MAIN_PATH']
    
    scrape.load_cultures(path)
    print("Cultures loaded.")
    scrape.load_religions(path)
    print("Religions loaded.")
    scrape.load_countries(path)
    print("Countries loaded.")
    scrape.load_provinces(path)
    print("Provinces loaded.")
    scrape.assign_areas_etc(path)
    print("Areas etc. set.")
    scrape.assign_trade_nodes(path)
    print("Trade nodes assigned.")
    scrape.load_and_assign_terrain(path)
    print("Terrain assidned.")
    scrape.load_and_assign_climate(path)
    print("Climate assigned.")
    scrape.misc_cleanup()
    print("Cleanup.")
    
    if DEFINES['MAP_PROVINCES']:
        print("Creating the province map.")
        province_map, image = create_province_map(DEFINES['MAIN_PATH'])
        # Warning: the lines below adds a minute or so of runtime.
        print("Determining neighbors.")
        get_neighbors(province_map) # Determines land and sea neighbors for all provinces.
        country_map(image, province_map, DEFINES['ORIGIN_PATH']) # Creates a country-view map for testing purposes, called testing.png
    
    if DEFINES['MAP_PROVINCES'] and DEFINES['OUTPUT']:
        save_info_as_csv('output')
        