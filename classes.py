from datetime import datetime

#%% Constants.
COLOR_DEFINES = {}

# Colors used for coloring in seas, wasteland, and uncolonized provinces.
COLOR_DEFINES['SEA_COLOR'] = (58, 202, 252)
COLOR_DEFINES['WASTELAND_COLOR'] = (64, 64, 64)
COLOR_DEFINES['UNCOLONIZED_COLOR'] = (128, 128, 128)

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
    color_dict = {}
    
    NEIGHBOR_OFFSETS = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    
    def __init__(self, prov_num, prov_name, color):
        self.__class__.instances.append(self)
        self.__class__.class_dict[int(prov_num)] = self
        self.__class__.color_dict[color] = self
        self.prov_num       = prov_num
        self.prov_name      = prov_name 
        self.color          = color
        self.owner          = 'None'
        self.is_city        = False
        self.EoA            = False
        self.has_port       = False
        self.cores          = []
        self.pixels         = []
        self.ingame         = False
        self.trade_good     = 'unknown'
        self.climate        = ''
        self.winter         = ''
        self.monsoon        = ''
        self.neighbors_all  = []
        self.neighbors_land = []
        self.neighbors_sea  = []
    
    def __repr__(self):
        return f'{self.prov_num} - {self.prov_name}' 
    
    def get_owner_color(self):
        if self.type == 'land':
            if self.owner != 'None':
                return self.owner.color
            else:
                return COLOR_DEFINES['UNCOLONIZED_COLOR']
        elif self.type == 'sea':
            return COLOR_DEFINES['SEA_COLOR']
        elif self.type == 'wasteland':
            return COLOR_DEFINES['WASTELAND_COLOR']
    
    def calc_development(self):
        try:
            self.development = self.base_manpower + self.base_production + self.base_manpower
        except:
            print(f'{self} has no development values. Assigning N/A to dev values.')
            self.development        = 'N/A'
            self.base_tax           = 'N/A'
            self.base_production    = 'N/A'
            self.base_manpower      = 'N/A'
            
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
                info_list[pos] = 'N/A'
                
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
                info_list[11] = 'Different religious group'

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
    
    def change_ownership(self, new_owner):
        try:
            self.owner.provinces.remove(self)
        except:
            pass
        try:
            self.owner = Country.tag_dict[new_owner]
            self.owner.provinces.append(self)
        except:
            pass
        
    # Getting border pixels.
    def get_neighbors(self, province_map):        
        # Set to store the border pixels
        border_pixels = set()
    
        # Convert the pixel_list to a set for faster lookups
        pixel_set = set(self.pixels)
    
        # Loop through each pixel belonging to the province.
        for pixel in self.pixels:
            x, y = pixel
    
            # Check each neighbor offset
            for offset_x, offset_y in self.__class__.NEIGHBOR_OFFSETS:
                neighbor_pixel = (x + offset_x, y + offset_y)
    
                # If the neighbor is not in the provided pixels list, it's a border pixel
                if neighbor_pixel not in pixel_set:
                    # Making sure that the neighboring pixel isn't above or below the map.
                    if neighbor_pixel[1] == -1 or neighbor_pixel[1] == 2048:
                        pass
                    
                    # If the neighboring pixel is left or right of the map, it should warp.
                    elif neighbor_pixel[0] == -1:
                        neighbor_pixel = (5632 - 1, y + offset_y)
                    elif neighbor_pixel[0] == 5632:
                        neighbor_pixel = (0, y + offset_y)
                    else:
                        border_pixels.add(neighbor_pixel)
                    
        border_owners = list({province_map[pixel] for pixel in border_pixels})

        for border_owner in border_owners:
            if border_owner.type == 'land':
                self.neighbors_all.append(border_owner)
                self.neighbors_land.append(border_owner)
            elif border_owner.type == 'sea':
                self.neighbors_all.append(border_owner)
                self.neighbors_sea.append(border_owner)


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
        self.color      = ''
        
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

# People.
class Person:
    def __init__(self, name, dynasty, adm, dip, mil, birth_date, female):
        self.__class__.instances.append(self)
        self.name = name.replace('"','')
        self.dynasty = dynasty.replace('"','')
        self.adm = int(adm)
        self.dip = int(dip)
        self.mil = int(mil)
        self.stats_sum = self.adm + self.dip + self.mil
        self.birth_date = birth_date
        self.female = female
        self.personality = []
        
        if self.birth_date != 'N/A':
            while len(self.birth_date.split('.')[0]) < 4:
                self.birth_date = '0' + self.birth_date
            self.calc_age()
        
        else:
            self.age = 'N/A'
    
    def calc_age(self):
        dob = datetime.strptime(self.birth_date, "%Y.%m.%d")
        start = datetime.strptime('1444.11.11', "%Y.%m.%d")
        
        delta = start - dob
        
        age = int(delta.days / 365)
        
        self.age = age
    
    def __repr__(self):
        return self.name

# Monarchs.
class Monarch(Person):
    instances = []

# Heirs.
class Heir(Person):
    instances = []

# Consorts.
class Consort(Person):
    instances = []
