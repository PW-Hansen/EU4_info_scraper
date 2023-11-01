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
DEFINES['MAP_PROVINCES'] = False
DEFINES['OUTPUT'] = True
DEFINES['ORIGIN_PATH'] = os.getcwd()
DEFINES['MAIN_PATH'] = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\Anbennar-PublicFork'


#%% Actually running stuff.
if __name__ == "__main__":
    scrape.load_cultures()
    scrape.load_religions()
    scrape.load_countries()
    scrape.load_provinces()
    scrape.assign_areas_etc()
    scrape.assign_trade_nodes()
    scrape.load_and_assign_terrain()
    scrape.load_and_assign_climate()
    scrape.misc_cleanup()
    
    if DEFINES['MAP_PROVINCES']:
        province_map, image = create_province_map(DEFINES['MAIN_PATH'])
        get_neighbors(province_map)
        country_map(image, province_map, DEFINES['ORIGIN_PATH'])
    
    if DEFINES['OUTPUT'] == True:
        save_info_as_csv('output')
        