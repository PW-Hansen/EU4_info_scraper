import os
import numpy as np
import re
import csv
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
ORIGIN_PATH = os.getcwd()


# MODE = 'anbennar'
# MAIN_PATH = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\Anbennar-PublicFork'
# PROVINCE_FLAG_FILE = 'anbennar_flags.eu4'
# CULTURE_FILE = "anb_cultures.txt" 
# RELIGION_FILE = '00_anb_religion.txt'
# COUNTRY_TAG_FILE = 'anb_countries.txt'

MODE = 'vanilla'
MAIN_PATH = r'D:\Steam\steamapps\common\Europa Universalis IV'
PROVINCE_FLAG_FILE = 'vanilla_flags.eu4'
CULTURE_FILE = '00_cultures.txt'
RELIGION_FILE = '00_religion.txt'
COUNTRY_TAG_FILE = '00_countries.txt'

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
        self.owner      = 'None'
        self.is_city    = False
        self.EoA        = False
        self.has_port   = False
        self.cores      = []
        self.pixels     = []
        self.ingame     = False
        self.climate    = ''
        self.winter     = ''
        self.monsoon    = ''
    
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
            
    def get_info(self):
        info_list = [None]*23
        self.calc_development()
        
        info_keys   = ['prov_num', 'development', 
                       'base_tax', 'base_production', 'base_manpower', 
                       'owner', 'trade_good', 'trade_node',
                       'terrain',
                       'religion', 'culture',
                       'is_city', 'has_port',
                       'climate', 'winter', 'monsoon',
                       'area', 'region', 'superregion', 'continent']
        
        info_pos    = [1, 2,
                       3, 4, 5,
                       6, 7, 8,
                       9,
                       10, 12,
                       14, 15,
                       16, 17, 18,
                       19, 20, 21, 22]
        
        prov_dict = self.__dict__ 
        
        # General information
        for key, pos in zip(info_keys, info_pos):
            if key in prov_dict:
                info_list[pos] = prov_dict[key]
            else:
                info_list[pos] = ''
        
        # Name
        info_list[0] = self.prov_name.split('_#')[0]
        
        # Religion status.
        if self.owner != 'None':
            owner = self.owner
            
            if self.religion == owner.religion:
                info_list[11] = 'Same religion'
            elif self.religion.group == owner.religion.group:
                info_list[11] = 'Same religious group'
            else:
                info_list[11] = 'Different culture group'

            if self.culture == owner.culture:
                info_list[13] = 'Same culture'
            elif self.culture.group == owner.culture.group:
                info_list[13] = 'Same culture group'
            else:
                info_list[13] = 'Different culture group'
            
        else:
            info_list[11] = 'N/A'
            info_list[13] = 'N/A'
        
        return info_list
    
                    
class Country(Behavior):
    instances = []
    class_dict = {}
    tag_dict = {}

    def __init__(self, tag, name):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.__class__.tag_dict[tag] = self
        self.tag        = tag
        self.name       = name
        self.provinces  = []
        
    def __repr__(self):
        return f'{self.tag} - {self.name}'
        
            
        
# Culture and religion classes.
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
        self.countries  = []
        
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
        self.countries  = []
        
        # Adds self to culture group.
        if self not in group.religions:
            group.religions.append(self)

# Map classes.
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
            
            for province in area.provinces:
                self.provinces.append(province)
                province.region = self
            

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
            for area in region.areas:
                area.superregion = self
                for province in area.provinces:
                    province.superregion = self
            
class Continent(Behavior):
    instances = []
    class_dict = {}

    def __init__(self, name, provinces):
        self.__class__.instances.append(self)
        self.__class__.class_dict[name] = self
        self.name = name
        self.provinces = provinces
        
        for province in provinces:
            province.continent = self



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
    
    if MODE == 'anbennar':
        exclude_tags = ['NAT', 'NPC', 'PAP', 'PIR', 'REB']  # Vanille remnants. Ignore. 
    elif MODE == 'vanilla':
        exclude_tags = []
    
    for country_file in country_files:
        if country_file[:3] not in exclude_tags:        
            country = Country(country_file[:3],country_file[6:-4])    
            countries.append(country)
            
    # Grabbing country colors.
    common_path = os.path.join(MAIN_PATH, 'common')
    os.chdir(common_path)
    
    common_path_countries = os.path.join(common_path, 'countries')
    os.chdir(common_path_countries)
    
    # country_colors_dict = {}
    
    # for file in os.listdir():
    #     with open(file, 'r', encoding = 'ANSI') as f:
    #         lines = f.readlines(100)
            
    #         country_name = file.split('.')[0]
            
    #         for line in lines:
    #             if 'color =' in line:
    #                 line.split('{')[1].split('}')[0]
    #                 rgb_vals = [int(val) for val in line.split('{')[1].split('}')[0].split(' ') if val != '']
    #                 color = (rgb_vals[0], rgb_vals[1], rgb_vals[2])
            
    #         country_colors_dict[country_name] = color

    common_path_country_tags = os.path.join(common_path, 'country_tags')
    os.chdir(common_path_country_tags)
    
    tag_country_file_dict = {}
    
    with open(COUNTRY_TAG_FILE, 'r', encoding = 'UTF-8') as f:
        lines = f.readlines()
        
        for line in lines:
            if '#' in line:
                line = line.split('#')[0]
            if '=' in line:
                line_split = line.split('=')
                tag = line_split[0].replace(' ','').replace('\t','')
                country_name = line_split[1].split('/')[1].split('.')[0]
                tag_country_file_dict[tag] = country_name        
            
    for country in countries:
        country.name = tag_country_file_dict[country.tag]
        # country.color = country_colors_dict[country.name]
        
    os.chdir(countries_path)
    
    country_dict = Country.tag_dict
    
    for country_file in os.listdir():
        country_tag = country_file[:3]
        country_info = read_PDX_file(os.getcwd(), country_file)
        
        if 'religion' and 'primary_culture' in country_info and country_tag not in exclude_tags:
            religion_string = country_info['religion'].split('#')[0]
            culture_string = country_info['primary_culture'].split('#')[0]
            country = country_dict[country_tag]
            
            if religion_string in Religion.class_dict:
                country_religion = Religion.class_dict[religion_string]

                country.religion = country_religion
                country_religion.countries.append(country)
            else:
                country.religion = 'not found'
                
            if culture_string in Culture.class_dict:
                country_culture = Culture.class_dict[culture_string]            
            
                country.culture = country_culture
                country_culture.countries.append(country)
            else:
                country.culture = 'not found'
            
        
        
    

#%% Cultures.
def load_cultures():
    common_path     = os.path.join(MAIN_PATH  ,'common')
    cultures_path   = os.path.join(common_path,'cultures')
    
    culture_info = read_PDX_file(cultures_path, CULTURE_FILE)
    
    not_cultures = ['graphical_culture', 'dynasty_names', 'male_names', 'female_names']
    
    for culture_group in culture_info:
        CultureGroup(culture_group)
        
        for sub_element in culture_info[culture_group]:
            if sub_element not in not_cultures:
                Culture(sub_element, CultureGroup.class_dict[culture_group])

    
def load_cultures_old():
    common_path     = os.path.join(MAIN_PATH  ,'common')
    cultures_path   = os.path.join(common_path,'cultures')
        
    # Cultures
    os.chdir(cultures_path)
    
    # Dict of culture groups and the cultures within them.
    culture_groups_dict = {}
    
    with open(CULTURE_FILE, 'r', encoding = 'ANSI') as f:
        lines = f.readlines()
        trimmed_lines = [line for line in lines if '\t\t' not in line[:2] and line != '\n' and line != '\t\n']
        
        culture_group   = ''
        cultures        = []
        
        for i,line in enumerate(trimmed_lines):
            if line[0] == '#': # Ignoring comments.
                pass
            elif line[0] != '\t' and '= {' in line:
                culture_group = line.split('=')[0].replace('\t','')
            elif '= {' in line and '_names' not in line: # Catches potential cultures.
                if '\t}\n' in trimmed_lines[i+1]: # Next line of cultures will always be a }.
                    potential_culture = line.replace('\t','\t ').split(' ')[1]
                    if '\t' not in potential_culture:
                        cultures.append(potential_culture)
                elif '}' in line:
                    potential_culture = line.replace('\t','\t ').split(' ')[1]
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

#%% Religions
def load_religions():
    common_path     = os.path.join(MAIN_PATH  ,'common')
    religions_path  = os.path.join(common_path,'religions')
    
    religion_info = read_PDX_file(religions_path, RELIGION_FILE)
    
    for religion_group in religion_info:
        ReligionGroup(religion_group)
        
        for sub_element in religion_info[religion_group]:
            if type(religion_info[religion_group][sub_element]) == dict:
                Religion(sub_element, ReligionGroup.class_dict[religion_group])


def load_religions_old():
    common_path     = os.path.join(MAIN_PATH  ,'common')
    religions_path  = os.path.join(common_path,'religions')
    os.chdir(religions_path)
            
    # Dict of religious groups and the religions within them.
    religion_groups_dict = {}
    
    with open(RELIGION_FILE, 'r', encoding = 'utf-8') as f:
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
            
#%% Getting areas, regions, continents, etc.
def prep_areas_etc():
    # Go to maps folder.
    map_path = os.path.join(MAIN_PATH,'map')
    
    os.chdir(map_path)
    
    # Figure out which provinces belongs to which areas.
    sea_provinces   = []
    land_provinces  = []
    
    with open("area.txt", 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        province_list = sea_provinces
        for i, line in enumerate(lines):
            # Stop when the deprecated areas are reached.
            if 'Deprecated' in line:
                break
    
            # Switches sea to False once a specific line has been reached.
            if MODE == 'anbennar':
                if 'Gerudia' in line:
                    province_list = land_provinces
            elif MODE == 'vanilla':
                if '#Land Areas' in line:
                    province_list = land_provinces
            
            if line[0] != '#':
                split_line = line.replace('\t','').replace('\n','').split(' ')
                for fragment in split_line:
                    if fragment not in ['','#']:
                        if fragment.isdigit():
                            province_list.append(int(fragment))
    
    return land_provinces, sea_provinces


#%% Provinces
def load_provinces(land_provinces, sea_provinces):
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
    
    country_dict = Country.tag_dict
    cultures_dict = Culture.class_dict
    religions_dict = Religion.class_dict
    
    for file_name in os.listdir():
        if file_name[0] != '~': # Duplicates, shouldn't be treated.     
            prov_num = int(file_name.split('-')[0].split('.')[0].split(' ')[0].replace(' ',''))
            
            province = provinces[prov_num]
            with open(file_name, 'r', encoding = 'latin-1') as f:
                lines = f.readlines()
                
                # Remove empty lines and comment lines.
                lines = [line for line in lines if line != '\n' and line[0] != '#']
                
                history = False
                
                for line in lines:
                    if not history:
                        line = line.replace('\n','').split('#')[0] # Making sure to avoid any comments.
                        if line[0].isdigit():
                            history = True
                            line = ''
                        
                        if '=' in line:
                            line_split = line.split('=')
                            key = line_split[0].replace(' ','')
                            value = line_split[1].replace(' ','')
                            value = value.replace('\t','').replace('{','').replace('}','')
                        
                        if 'owner' in key:
                            province.owner = country_dict[value]
                            country_dict[value].provinces.append(province)
                        elif 'controller' in key:
                            province.controller = country_dict[value]
                        elif 'add_core' in key:
                            province.cores.append(country_dict[value])
                        elif 'culture' in key:
                            value = value.replace('discovered_by','') # Goddammit PDX.
                            
                            province.culture = cultures_dict[value]
                            cultures_dict[value].provinces.append(province)
                            cultures_dict[value].group.provinces.append(province)
                        elif 'religion' in key:
                            value = value.replace('"','') # Why do I need to do this, PDX?
                            
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
            province.ingame = True
    
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
def assign_areas_etc():
    map_path = os.path.join(MAIN_PATH,'map')
    
    area_info = read_PDX_file(map_path, 'area.txt')
    
    for name in area_info:
        if len(area_info[name]) != 0:
            if 'color' in area_info[name][0]:
                province_string = area_info[name][1]
            else:
                province_string = area_info[name][0]
            
            provinces = get_province_numbers(province_string)
            Area(name, provinces)
    
    region_info = read_PDX_file(map_path, 'region.txt')
    
    for name in region_info:
        if type(region_info[name]) == dict:
            if len(region_info[name]['areas'][0]) > 1:
                areas_string = region_info[name]['areas']
                areas = []
                for area_string in areas_string:
                    area_string = area_string.replace('\n','').replace('\t','').replace(' ','').split('#')[0]
                    if 'area' in area_string and area_string in Area.class_dict:
                        area = Area.class_dict[area_string]
                    
                    areas.append(area)
                    
                Region(name, areas)

    superregion_info = read_PDX_file(map_path, 'superregion.txt')
    
    for name in superregion_info:
        regions = []
        for string in superregion_info[name]:
            if '_region' in string:
                region_string = string.replace('\n','').replace('\t','').replace(' ','').split('#')[0]
                
                if '_region' in region_string and region_string in Region.class_dict:
                    regions.append(Region.class_dict[region_string])
        
        if len(regions) > 0:
            Superregion(name, regions)

    continent_info = read_PDX_file(map_path, 'continent.txt')
    
    ignore_continents = ['island_check_provinces'] # Just four provinces which already have a continent.
    
    for name in continent_info:
        if name not in ignore_continents:
            province_string = ''.join(continent_info[name]).replace('\n',' ')
            provinces = get_province_numbers(province_string)
            
            Continent(name, provinces)
        


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
                
                
            if log_provinces: 
                if '}' in line: # If a bracket is closed, stop logging and don't count provinces.
                    log_provinces = False

                else: # Otherwise, add the provinces to node_provinces.
                    node_provinces += line.replace('\t',' ').replace('\n','').split(' ')
                
            if 'members' in line: # Next line is going to contain member provinces.
                log_provinces = True
                    
            if line[0] == '}': # The entry for the trade node is over. Define the node.
                node_prov_nums = [int(province) for province in node_provinces if province != '']
                node_provinces = [Province.class_dict[prov_num] for prov_num in node_prov_nums]
                Tradenode(node_name, node_provinces, outgoing)

    # Have nodes actually connect to each other.
    for node in Tradenode.instances:
        outgoing = node.outgoing
        outgoing_nodes = []
        
        for value in outgoing:
            outgoing_node = Tradenode.class_dict[value]
            outgoing_nodes.append(outgoing_node)
            outgoing_node.incoming.append(node)
            
        node.outgoing = outgoing_nodes
            
#%% Setting up terrain and assigning it to provinces.
def load_and_assign_terrain():
    terrain_file_dict = read_PDX_file(os.path.join(MAIN_PATH, 'map'), 'terrain.txt')

    terrain_types = terrain_file_dict['categories']
    k, v = [], []

    terrain_province_dict = {}
    
    ignore_list = ['pti', 'ocean', 'inland_ocean', 'impassable_mountains']
    
    for key in terrain_types:
        if key not in ignore_list:
            k.append(key)
            v.append(terrain_types[key])
            
            terrain_province_dict[key] = ''
    
    
    os.chdir(ORIGIN_PATH)
    
    with open(PROVINCE_FLAG_FILE, 'r', encoding = 'ANSI') as f:
        lines = f.readlines()
        
        for i,line in enumerate(lines):
            if 'terrain_is_' in line:
                terrain_key = line.split('terrain_is_')[1].split('=')[0]
                
                # Goes upwards until a province number is detected.
                j = i
                while lines[j][0] != '-':
                    j -= 1
                
                province_num = lines[j].split('-')[1].split('=')[0]
                
                terrain_province_dict[terrain_key] += province_num + ' '
            
            if 'province_has_port' in line:
                # Goes upwards until a province number is detected.
                j = i
                while lines[j][0] != '-':
                    j -= 1
                
                province_num = lines[j].split('-')[1].split('=')[0]
                
                Province.class_dict[int(province_num)].has_port = True
                
    
        
    for key, value in zip(k,v):
        name = key
        try:
            dev_cost = value['local_development_cost']
        except:
            dev_cost = 0
        
        provinces = get_province_numbers(terrain_province_dict[key])
        
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

        override_string = ''.join(value).replace('\n', ' ').replace('\t',' ')
        provinces = get_province_numbers(override_string)
        
        Climate(name, provinces)
        
    # Default climates: temperate, no winter, no monsoon
    temperate_provinces     = []
    no_winter_provinces     = []
    no_monsoon_provinces    = []
    
    for province in Province.instances:
        if province.ingame and province.type == 'land':
            if province.climate == '':
                temperate_provinces.append(province)
            if province.winter == '':
                no_winter_provinces.append(province)
            if province.monsoon == '':
                no_monsoon_provinces.append(province)
                
    Climate('temperate', temperate_provinces)
    Climate('no_winter', no_winter_provinces)
    Climate('no_monsoon', no_monsoon_provinces)
    

#%% Information extraction.
def save_info_as_csv(csv_name):
    header  = ['Province name','Province number', 'Development', 
               'Base Tax', 'Base Production', 'Base manpower', 
               'Owner', 'Trade good', 'Trade node',
               'Terrain',
               'Religion', 'Owner religious status', 
               'Culture', 'Owner cultural status',
               'Colonized', 'Has port',
               'Climate', 'Winter', 'Monsoon',
               'Area', 'Region', 'Superregion', 'Continent']
    
    provinces_info = [header]
    
    for province in Province.instances:
        if province.ingame and province.type == 'land':
            provinces_info.append(province.get_info())
            
    os.chdir(ORIGIN_PATH)        
    
    with open(csv_name + '.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(provinces_info)
            
        

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
        if '=' in lines[start]:
            key = lines[start].split('=', 1)[0].replace(' ','')
            value = lines[start + 1 : end]
            for i,line in enumerate(value):
                if line[0] == '\t':
                    value[i] = line[1:]
            
            components[key] = read_PDX_file_subfunction(value)
        
    for line in lines:
        if '=' in line and '{' not in line and '}' not in line and line[0] not in ['#', '\t']:
            key,value = line.replace(' ','').replace('\t','').replace('\n','').split('=', 1)
            components[key] = value
            
    # for line in lines:
    #     if '=' in line and '{' in line and '}' in line:
    #         key, value = line.split('=', 1)
    #         key.replace(' ','')
    #         components[key] = value
            
    
    if len(components) == 0:
        components = lines         
        
    return components

def read_PDX_file(path, filename):
    os.chdir(path)
    
    with open(filename, 'r', encoding = 'ansi') as f:
        lines = f.readlines()
    
    return read_PDX_file_subfunction(lines)


#%% Actually running stuff.
load_cultures()
load_religions()
load_countries()
land_provinces, sea_provinces = prep_areas_etc()
load_provinces(land_provinces, sea_provinces)
assign_areas_etc()
assign_trade_nodes()
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