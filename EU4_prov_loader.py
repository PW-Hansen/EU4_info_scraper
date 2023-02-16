import os
import numpy as np
import re
# from PIL import Image
# import imageio

#%% TO-DO
# Country values, such as culture and religion.
# Grab ruler stats
# Tag colors
# Technology groups?
# Country flags
# Trade goods, also change the province write function to reflect this
# Tribal lands?

#%% Paths
origin_path = os.getcwd()
MAIN_PATH = r'D:\Steam\steamapps\workshop\content\236850\1385440355'


#%% Constants
SEA_COLOR = (58, 202, 252)
WASTELAND_COLOR = (64, 64, 64)
UNCOLONIZED_COLOR = (128, 128, 128)


#%%
class Behavior:
    def __repr__(self):
        return self.name

    def calc_total_dev(self):
        self.total_dev = 0
        for province in self.provinces:
            try:
                province.calc_development()
                self.total_dev += province.development
            except:
                print('Something went wrong with province {province.prov_num}!')
        return self.total_dev
    
    def calc_average_dev(self):
        try:
            self.avg_dev = round(self.total_dev / len(self.provinces),2)
            return self.avg_dev
        except:
            self.calc_total_dev()
            self.avg_dev = round(self.total_dev / len(self.provinces),2)      
            return self.avg_dev
            
class Province():
    instances = []
    class_dict = {}
    
    def __init__(self, prov_num, prov_name, color):
        self.__class__.instances.append(self)
        self.__class__.class_dict[int(prov_num)] = self
        self.prov_num   = prov_num
        self.prov_name  = prov_name 
        self.color      = color
        self.is_city    = False
        self.EoA        = False
        self.cores      = []
        self.pixels     = []
        self.climate    = 'Temperate'   # Default
        self.winter     = 'No winter'   # Default
        self.monsoon    = 'No monsoon'  # Default
    
    def __repr__(self):
        return f'{self.prov_num} - {self.prov_name}' 
    
    def get_owner_color(self):
        if self.type == 'land':
            if hasattr(self, 'owner'):
                return self.owner.color
            else:
                return UNCOLONIZED_COLOR
        elif self.type == 'sea':
            return SEA_COLOR
        elif self.type == 'wasteland':
            return WASTELAND_COLOR
    
    def calc_development(self):
        try:
            self.development = self.base_manpower + self.base_production + self.base_manpower
        except:
            print('Tried to calculate development of a province without development.')
    
                    
class Country(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, tag, name):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.tag        = tag
        self.name       = name
        self.provinces  = []
        
    def __repr__(self):
        return f'{self.tag} - {self.name}'
        
            
        
# Culture and religion could be the same thing, but are kept seperate in case
# I want to implement anything specific for any of them.
class CultureGroup(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name       = name
        self.cultures   = []
        self.provinces  = []

class Culture(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, group):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.group = group
        self.provinces  = []
        
        # Adds self to culture group.
        if self not in group.cultures:
            group.cultures.append(self)

class ReligionGroup(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name       = name
        self.religions  = []
        self.provinces  = []

class Religion(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, group):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.group = group
        self.provinces  = []
        
        # Adds self to culture group.
        if self not in group.religions:
            group.religions.append(self)

# Map classes. Also kept seperate in case of future functionality.
class Area(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, provinces):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.provinces = provinces

        self.region = 'TBD'
        
        for province in provinces:
            province.area = self
        

class Region(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, areas):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.areas = areas

        self.provinces  = []
        self.superregion = 'TBD'
        
        for area in areas:
            area.region = self
            

class Superregion(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, regions):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.regions = regions

        self.provinces  = []
        
        for region in regions:
            region.superregion = self
            

# Trade node class
class Tradenode(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, provinces, outgoing):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.provinces = provinces
        self.outgoing = outgoing
        self.incoming = []
        
        for province in provinces:
            province.trade_node = self
    
# Terrrain class
class Terrain(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, provinces, local_dev_cost):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.provinces = provinces
        self.local_dev_cost = local_dev_cost
        
        for province in provinces:
            province.terrain = self
    
# Climate class
class Climate(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, provinces):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.provinces = provinces
        
        for province in provinces:
            if 'winter' in name:
                province.winter = self
            elif 'monsoon' in name:
                province.monsoon = self
            else:
                province.climate = self


#%% Load countries.
def load_countries():
    history_path    = os.path.join(MAIN_PATH, 'history')
    countries_path  = os.path.join(history_path, 'countries')
    
    os.chdir(countries_path)
    
    country_files = os.listdir()
    countries = []
    
    exclude_tags = ['NAT', 'NPC', 'PAP', 'PIR', 'REB']
    
    for country_file in country_files:
        if country_file[:3] not in exclude_tags:        
            country = Country(country_file[:3],country_file[6:-4])    
            countries.append(country)
    
    # Make future lookup easier.
    country_dict = {}
    for country in countries:
        country_dict[country.tag] = country
        
        
    # Grabbing country colors.
    common_path = os.path.join(MAIN_PATH, 'common')
    os.chdir(common_path)
    
    common_path_countries = os.path.join(common_path, 'countries')
    os.chdir(common_path_countries)
    
    country_colors_dict = {}
    
    for file in os.listdir():
        with open(file, 'r', encoding = 'ANSI') as f:
            lines = f.readlines(100)
            
            country_name = file.split('.')[0]
            
            for line in lines:
                if 'color =' in line:
                    line.split('{')[1].split('}')[0]
                    rgb_vals = [int(val) for val in line.split('{')[1].split('}')[0].split(' ') if val != '']
                    color = (rgb_vals[0], rgb_vals[1], rgb_vals[2])
            
            country_colors_dict[country_name] = color
    
    common_path_country_tags = os.path.join(common_path, 'country_tags')
    os.chdir(common_path_country_tags)
    
    tag_country_file_dict = {}
    
    with open('anb_countries.txt', 'r', encoding = 'UTF-8') as f:
        lines = f.readlines()
        
        for line in lines:
            if '#' in line:
                line = line.split('#')[0]
            if '=' in line:
                line_split = line.split('=')
                tag = line_split[0].replace(' ','')
                country_name = line_split[1].split('/')[1].split('.')[0]
                tag_country_file_dict[tag] = country_name
    
            
    for country in countries:
        country.name = tag_country_file_dict[country.tag]
        country.color = country_colors_dict[country.name]
        
    return country_dict


#%% Cultures.
def load_cultures():
    common_path     = os.path.join(MAIN_PATH  ,'common')
    cultures_path   = os.path.join(common_path,'cultures')
    
    # Cultures
    os.chdir(cultures_path)
    
    # Dict of culture groups and the cultures within them.
    culture_groups_dict = {}
    
    with open("anb_cultures.txt", 'r', encoding = 'ANSI') as f:
        lines = f.readlines()
        trimmed_lines = [line for line in lines if '\t\t' not in line[:2] and line != '\n' and line != '\t\n']
        
        culture_group   = ''
        cultures        = []
        
        for i,line in enumerate(trimmed_lines):
            if line[0] == '#': # Ignoring comments.
                pass
            elif line[0] != '\t' and '= {' in line:
                culture_group = line.split(' ')[0]
            elif '= {' in line and '_names' not in line: # Catches potential religions.
                if '\t}\n' in trimmed_lines[i+1]: # Next line of religions will always be a }.
                    potential_culture= line.replace('\t','\t ').split(' ')[1]
                    if '\t' not in potential_culture:
                        cultures.append(potential_culture)
            elif line[0] != '\t' and '}' in line:
                culture_groups_dict[culture_group] = cultures
                cultures = []
    
    culture_groups_dict.pop('') # Removing empty element
    
    culture_groups  = []
    cultures        = []
    
    for group in culture_groups_dict:
        culture_group = CultureGroup(group)
        culture_groups.append(culture_group)
        for sub_culture in culture_groups_dict[group]:
            culture = Culture(sub_culture,culture_group)
            cultures.append(culture)
    
    # Make future lookup easier.
    cultures_dict = {}
    for culture in cultures:
        cultures_dict[culture.name] = culture
        
    return cultures_dict

#%% Religions
def load_religions():
    common_path     = os.path.join(MAIN_PATH  ,'common')
    religions_path  = os.path.join(common_path,'religions')
    os.chdir(religions_path)
            
    # Dict of religious groups and the religions within them.
    religion_groups_dict = {}
    
    with open("00_anb_religion.txt", 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        trimmed_lines = [line for line in lines if '\t\t' not in line and line != '\n']
        
        religious_group = ''
        religions = []
        
        for i,line in enumerate(trimmed_lines):
            if line[0] == '#': # Ignoring comments.
                pass
            elif line[0] != '\t' and '= {' in line:
                religious_group = line.split(' ')[0]
            elif '= {' in line: # Catches potential religions.
                if '\t}\n' in trimmed_lines[i+1]: # Next line of religions will always be a }.
                    potential_religion = line.replace('\t','\t ').split(' ')[1]
                    if '\t' not in potential_religion:
                        religions.append(potential_religion)
            elif line[0] != '\t' and '}' in line:
                religion_groups_dict[religious_group] = religions
                religions = []
    
    # Anbennar apparently has animism, will be added manually.
    religion_groups_dict['pagan'] = ['animism']
    
    religion_groups  = []
    religions        = []
    
    for group in religion_groups_dict:
        religion_group = ReligionGroup(group)
        religion_groups.append(religion_group)
        for religion_branch in religion_groups_dict[group]:
            religion = Religion(religion_branch,religion_group)
            religions.append(religion)
    
    # Make future lookup easier.
    religions_dict = {}
    for religion in religions:
        religions_dict[religion.name] = religion

    return religions_dict
        
#%% Getting areas, regions, continents, etc.
def prep_areas_etc():
    # Go to maps folder.
    map_path = os.path.join(MAIN_PATH,'map')
    
    os.chdir(map_path)
    
    # Figure out which provinces belongs to which areas.
    sea_provinces   = []
    land_provinces  = []
    areas_dict = {}
    
    with open("area.txt", 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        province_list = sea_provinces
        for i, line in enumerate(lines):
            # Stop when the deprecated areas are reached.
            if 'Deprecated' in line:
                break
    
            # Switches sea to False once the line containing Gerudia has been
            # reaches.
            if 'Gerudia' in line:
                province_list = land_provinces
            
            split_line = line.replace('\t','').replace('\n','').split(' ')
            try: 
                for fragment in split_line:
                    province_list.append(int(fragment))
            except:
                pass
            
            if '_area = {' in line:
                area_name = line.replace('\t','').replace('\n','').replace(' ','').split('=')[0]
                
                # Checks that the area isn't commented out.
                if area_name[0] != '#':
                    area_provinces = lines[i+1].replace('\t','').replace('\n','').split(' ')
                    area_provinces = [area_province for area_province in area_provinces if area_province != '']
                    areas_dict[area_name] = area_provinces
                
    
    # Figure out which areas belongs to which regions.
    regions_dict = {}
    
    with open("region.txt", 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        lines = lines[10:] # Skips the first ten lines, as to avoid the random_new_world_region.
    
        addition = False
        region_areas = []
    
        for line in lines:
            # Stop when the debug region is reached.
            if 'debug' in line:
                break
            
            # If a region is detected, declare that the new region.
            if '_region' in line:
                addition = True
                new_region = line.replace('\t','').replace('\n','').replace(' ','').split('=')[0]
            # If a } is detected it means no more areas for the current regions, so stop adding to it
            # and put it into the region dictionary.
            elif '}' in line and addition:
                addition = False
                regions_dict[new_region] = region_areas
                region_areas = []
                
            if addition:
                potential_area = line.replace('\t','').replace('\n','').replace(' ','').split('=')[0]
                if '_area' in potential_area:
                    region_areas.append(potential_area)
                  
    # Figure out which regions belongs to which superregions.
    superregions_dict = {}
    
    with open("superregion.txt", 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    
        addition = False
        superregion_regions = []
    
        for line in lines:
            # If a region is detected, declare that the new region.
            if '_superregion' in line:
                addition = True
                new_superregion = line.replace('\t','').replace('\n','').replace(' ','').split('=')[0]
            # If a } is detected it means no more regions for the current superregions, so stop adding to it
            # and put it into the superregion dictionary.
            elif '}' in line and addition:
                addition = False
                # We don't want empty superregions.
                if len(superregion_regions)>0:
                    superregions_dict[new_superregion] = superregion_regions
                    superregion_regions = []
                
            if addition:
                potential_region = line.replace('\t','').replace('\n','').replace(' ','').split('=')[0]
                if '_region' in potential_region:
                    superregion_regions.append(potential_region)
    
    return land_provinces, sea_provinces, areas_dict, regions_dict, superregions_dict


#%% Provinces
def load_provinces(country_dict, cultures_dict, religions_dict, land_provinces, sea_provinces):
    history_path    = os.path.join(MAIN_PATH   ,'history')
    provinces_path  = os.path.join(history_path,'provinces')
    map_path = os.path.join(MAIN_PATH,'map')
    
    os.chdir(map_path)
    
    
    # Getting province definitions, then loading their RGB values into a list so 
    # that the ith entry in the list corresponds to province number i.
    with open('definition.csv', 'r') as f:
        lines = f.readlines()
        province_definitions = {}
    
        provinces = [None] * len(lines)
    
        for line in lines[1:]:
            line_fragments = line.split(';')
            prov_num = int(line_fragments[0])
            r = int(line_fragments[1])
            g = int(line_fragments[2])
            b = int(line_fragments[3])
            prov_name = line_fragments[4]
            color = (r, g, b)
            province_definitions[color] = prov_num
            
            province = Province(prov_num, prov_name, color)
            province.color = color
            
            provinces[prov_num] = province
            
    os.chdir(provinces_path)
    
    
    for file_name in os.listdir():
        if file_name[0] != '~': # Duplicates, shouldn't be treated.     
            prov_num = int(file_name.split(' ')[0])
            
            province = provinces[prov_num]
            with open(file_name, 'r', encoding = 'latin-1') as f:
                lines = f.readlines()
                
                # Remove empty lines and comment lines.
                lines = [line for line in lines if line != '\n' and line[0] != '#']
                
                for line in lines:
                    line = line.replace('\n','').split('#')[0] # Making sure to avoid any comments.
                    
                    if '=' in line:
                        line_split = line.split('=')
                        key = line_split[0].replace(' ','')
                        value = line_split[1].replace(' ','')
                    
                    if 'owner' in key:
                        province.owner = country_dict[value]
                        country_dict[value].provinces.append(province)
                    elif 'controller' in key:
                        province.controller = country_dict[value]
                    elif 'add_core' in key:
                        province.cores.append(country_dict[value])
                    elif 'culture' in key:
                        province.culture = cultures_dict[value]
                        cultures_dict[value].provinces.append(province)
                        cultures_dict[value].group.provinces.append(province)
                    elif 'religion' in key:
                        province.religion = religions_dict[value]
                        religions_dict[value].provinces.append(province)
                        religions_dict[value].group.provinces.append(province)
                    elif 'hre' in key:
                        if value == 'yes':
                            province.EoA = True
                    elif 'center_of_trade' in key:
                        province.CoT = int(value)
                    elif 'trade_good' in key: # Make trade goods a class too?
                        province.trade_good = value
                    elif 'is_city' in key and value == 'yes':
                        province.is_city = True
                    elif 'base_tax' in key:
                        province.base_tax = int(value)
                    elif 'base_production' in key:
                        province.base_production = int(value)
                    elif 'base_manpower' in key:
                        province.base_manpower = int(value)
        
            provinces[prov_num] = province
    
    # Setting land/sea/wasteland definition of provinces.
    for prov in land_provinces:
        if type(provinces[prov]) != type(None):
            provinces[prov].type = 'land'
    
    for prov in sea_provinces:
        if type(provinces[prov]) != type(None):
            provinces[prov].type = 'sea'
    
    for province in provinces:
        if type(province) != type(None):
            if not hasattr(province, 'type'):
                province.type = 'wasteland'
                
                
#%% Areas, regions, and superregions.
def assign_areas_etc(areas_dict):
    provinces = Province.instances
    
    for area in areas_dict:
        area_provinces = [provinces[int(prov_num) - 1] for prov_num in areas_dict[area]]
        
        # There are apparently "relic" provinces in some areas. Must be removed.
        while None in area_provinces:
            # print(area)   # Will spam the console. Maybe due to Sarhal?
            area_provinces.remove(None)
        
        Area(area,area_provinces)
    

# TODO: regions, superregions.

#%% Trade node
def assign_trade_nodes():
    # Getting correct directionary.
    common_path = os.path.join(MAIN_PATH, 'common')
    os.chdir(common_path)
    
    common_path_tradenodes = os.path.join(common_path, 'tradenodes')
    os.chdir(common_path_tradenodes)

    with open("00_tradenodes.txt", 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        
        log_provinces = False
        
        for i, line in enumerate(lines):
            if line[0] not in ['\t', '}']: # Start of a trade node.
                node_name = line.split('={')[0]
                
                node_provinces = []
                outgoing = []
            
            if 'outgoing={' in line: # About to list a new node.
                outgoing_node = lines[i+1].split("=")[1].replace('\t','').replace('\n','').replace('"','')
                
                outgoing.append(outgoing_node)
                
            if 'members' in line: # Next line is going to contain member provinces.
                log_provinces = True
                
            if log_provinces: 
                if '}' in line: # If a bracket is closed, stop logging and don't count provinces.
                    log_provinces = False

                else: # Otherwise, add the provinces to node_provinces.
                    node_provinces = line.replace('\t','').replace('\n','').split(' ')
                
                    
            if line[0] == '}': # The entry for the trade node is over. Define the node.
                node_prov_nums = [int(province) for province in node_provinces if province != '']
                node_provinces = [Province.instances[prov_num - 1] for prov_num in node_prov_nums]
                Tradenode(node_name, node_provinces, outgoing)

    # Create dictionary for easier look-up.
    trade_node_dict = {}    
    for node in Tradenode.instances:
        trade_node_dict[node.name] = node

    # Have nodes actually connect to each other.
    for node in Tradenode.instances:
        outgoing = node.outgoing
        outgoing_nodes = []
        
        for value in outgoing:
            outgoing_node = trade_node_dict[value]
            outgoing_nodes.append(outgoing_node)
            outgoing_node.incoming.append(node)
            
        node.outgoing = outgoing_nodes
        
    return trade_node_dict
    
#%% Setting up terrain and assigning it to provinces.
def load_and_assign_terrain():
    terrain_file_dict = read_PDX_file(os.path.join(MAIN_PATH, 'map'), 'terrain.txt')

    terrain_types = terrain_file_dict['categories']
    k, v = [], []
    
    ignore_list = ['pti', 'ocean', 'inland_ocean', 'impassable_mountains']
    
    for key in terrain_types:
        if key not in ignore_list:
            k.append(key)
            v.append(terrain_types[key])
        
        
    for key, value in zip(k,v):
        name = key
        try:
            dev_cost = value['local_development_cost']
        except:
            dev_cost = 0
        
        override_string = ''.join(value['terrain_override']).replace('\n', ' ')
        provinces = get_province_numbers(override_string)
        
        Terrain(name, provinces, dev_cost)

#%% Climate
def load_and_assign_climate():
    climate_file_dict = read_PDX_file(os.path.join(MAIN_PATH, 'map'), 'climate.txt')

    k, v = [], []
        
    ignore_list = ['equator_y_on_province_image', 'impassable']
    
    for key in climate_file_dict:
        if key not in ignore_list:
            k.append(key)
            v.append(climate_file_dict[key])
    
    for key, value in zip(k,v):
        name = key

        override_string = ''.join(value).replace('\n', ' ')
        provinces = get_province_numbers(override_string)
        
        Climate(name, provinces)

#%% PDX file reader and other general helper functions
def get_province_numbers(string):
    # Takes a string of province numbers, which may also have comments and the
    # like, and returns a list of references with the appropriate Province 
    # class objects.
    cleaned_string = re.sub("[^0-9 ]", "", string) # Removes everything but numbers and spaces.
    province_nums = [int(province) for province in cleaned_string.split(' ') if len(province) != 0]
    provinces = [Province.class_dict[prov_num] for prov_num in province_nums]

    return provinces
    

def read_PDX_file_subfunction(lines):
    ranges_start = []
    ranges_end   = []
    
    for i,line in enumerate(lines):
        if '{' in line and '}' not in line and line[0] not in ['\t','#']:
            ranges_start.append(i)
        if line[0] == '}':
            ranges_end.append(i)
    
    components = {}
    
    for start, end in zip(ranges_start, ranges_end):
        key = lines[start].split('=')[0].replace(' ','')
        value = lines[start + 1 : end]
        for i,line in enumerate(value):
            if line[0] == '\t':
                value[i] = line[1:]
        
        components[key] = read_PDX_file_subfunction(value)
        
    for line in lines:
        if '=' in line and '{' not in line and '}' not in line and line[0] not in ['#', '\t']:
            key,value = line.replace(' ','').replace('\t','').replace('\n','').split('=')
            components[key] = value
    
    if len(components) == 0:
        components = lines         
        
    return components

def read_PDX_file(path, filename):
    os.chdir(path)
    
    with open(filename, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
    
    return read_PDX_file_subfunction(lines)


#%% Actually running stuff.
country_dict = load_countries()
cultures_dict = load_cultures()
religions_dict = load_religions()
land_provinces, sea_provinces, areas_dict, regions_dict, superregions_dict = prep_areas_etc()
load_provinces(country_dict, cultures_dict, religions_dict, land_provinces, sea_provinces)
assign_areas_etc(areas_dict)
trade_node_dict = assign_trade_nodes()
load_and_assign_terrain()
load_and_assign_climate()

#%% Loading map.
if False:
    os.chdir(map_path)
    
    im = Image.open('provinces.bmp')
    province_map = im.load()
    
    x,y = im.size
    
    province_map_indexed = np.zeros((x,y))
    province_map_provinces = np.zeros((x,y), dtype = Province)
    for i in range(x):
        for j in range(y):
            pixel_color = province_map[i,j]
            index = int(province_definitions[pixel_color])
            province_map_indexed[i,j] = index
            province_map_provinces[i,j] = provinces[index]
            provinces[index].pixels.append([i,j])
        
        
#%%
if False:
    os.chdir(origin_path)
    
    xmax,ymax=im.size
    
    for x in range(xmax):
        for y in range(ymax):
            province_map[x,y] = province_map_provinces[x,y].get_owner_color()
    
    imageio.imwrite('testing.png', im)