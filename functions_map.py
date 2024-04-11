import os
import numpy as np
from PIL import Image
from classes import Province
from functions import save_info_as_csv

#%% Constants.


#%% Creating province map.
def create_province_map(main_path):
    map_path = os.path.join(main_path,'map')
    
    os.chdir(map_path)
    
    im = Image.open('provinces.bmp')
    province_map_raw = im.load()
    
    x, y = im.size
    province_dict = Province.color_dict
    province_map = np.zeros((x,y), dtype = Province)
    
    for i in range(x):
        for j in range(y):
            pixel_color = province_map_raw[i,j]
            province = province_dict[pixel_color]
            province_map[i,j] = province
            province.pixels.append((i,j))        
            
    return province_map, im

#%% Getting neighbors for land and sea provinces.
def get_neighbors(province_map):    
    for province in Province.instances:
        if province.type != 'wasteland':
            province.get_neighbors(province_map)   
    
#%% Map output.
# Outputting a map. Takes a map of all provinces and inputs the proper colors
# for a political map, i.e. owner's color for owned provinces, blue for sea,
# and grey for unowned.
def country_map(im, province_map, origin_path):
    os.chdir(origin_path)
    
    xmax, ymax = im.size
    
    output_im = Image.new('RGB', (xmax, ymax))
            
    for x in range(xmax):
        for y in range(ymax):
            rgb = province_map[x,y].get_owner_color()
            output_im.putpixel((x, y), rgb)
    
    output_im.save('testing.png')