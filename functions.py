import os
import re
import csv

from classes import Province, Country, CultureGroup, Culture, ReligionGroup, Religion, Area, Region, Superregion, Continent, Tradenode, Terrain, Climate, Person, Monarch, Heir, Consort

#%% Constants.
DEFINES = {}

DEFINES['ORIGIN_PATH'] = os.getcwd()


#%% Misc. cleanup.
def misc_cleanup():
    for country in Country.instances:
        if hasattr(country, 'capital'):
            if type(country.capital) == int:
                country.capital = Province.class_dict[country.capital]

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
            
    os.chdir(DEFINES['ORIGIN_PATH'])        
    
    with open(csv_name + '.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(provinces_info)

def export_rulers_etc(csv_name):
    header = ['Total mana' , 'TAG', 'Tag name', 'ADM/DIP/MIL', 'Age', 'Personalities', 'Name', 'Dynasty', 'Gender', 'Country region', 'Country superregion']
    
    ruler_data = [header]
    for monarch in Monarch.instances:
        if len(monarch.country.provinces) > 0:        
            statline = f'{monarch.adm}/{monarch.dip}/{monarch.mil}'
            
            ruler_info = [monarch.stats_sum, monarch.country.tag, 
                          monarch.country.name, statline, monarch.age,
                          monarch.personality, monarch.name, monarch.dynasty]
            
            country_capital = Province.class_dict[monarch.country.capital]
            
            ruler_info.append(country_capital.region)
            ruler_info.append(country_capital.superregion)
            
            if monarch.female == 'yes':
                ruler_info.append('Female')
            else:
                ruler_info.append('Male')
            
            ruler_data.append(ruler_info)

    with open(csv_name + '_rulers.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(ruler_data)
        
    heir_data = [header]
    for heir in Heir.instances:
        if len(heir.country.provinces) > 0:        
            statline = f'{heir.adm}/{heir.dip}/{heir.mil}'
            
            heir_info = [heir.stats_sum, heir.country.tag,
                         heir.country.name, statline, heir.age,
                         heir.personality, heir.name, heir.dynasty]
            
            country_capital = Province.class_dict[heir.country.capital]
            
            heir_info.append(country_capital.region)
            heir_info.append(country_capital.superregion)

            if heir.female == 'yes':
                heir_info.append('Female')
            else:
                heir_info.append('Male')

            heir_data.append(heir_info)

    with open(csv_name + '_heirs.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(heir_data)
        
    header.append('Country of origin')
    consort_data = [header]
    for consort in Consort.instances:
        if len(consort.country.provinces) > 0:        
            statline = f'{consort.adm}/{consort.dip}/{consort.mil}'
            
            consort_info = [consort.stats_sum, consort.country.tag, 
                            consort.country.name, statline, consort.age,
                            consort.personality, consort.name, consort.dynasty]
            
            country_capital = Province.class_dict[consort.country.capital]
            
            consort_info.append(country_capital.region)
            consort_info.append(country_capital.superregion)

            if consort.female == 'yes':
                consort_info.append('Female')
            else:
                consort_info.append('Male')
                
            consort_info.append(consort.origin)

            consort_data.append(consort_info)

    with open(csv_name + '_consorts.csv', 'w', newline = '') as f:
        writer = csv.writer(f)
        writer.writerows(consort_data)


#%% PDX file reader and other general helper functions
def get_province_numbers(string):
    # Takes a string of province numbers, which may also have comments and the
    # like, and returns a list of references with the appropriate Province 
    # class objects.
    cleaned_string = re.sub("[^0-9 ]", "", string) # Removes everything but numbers and spaces.
    province_nums = [int(province) for province in cleaned_string.split(' ') if len(province) != 0]
    provinces = [Province.class_dict[prov_num] for prov_num in province_nums]

    return provinces
    
# Is a bit wonky with dictionaries, can overwrite stuff if working with, i.e.
# save files where there are multiple entries for the same date. Future fix?
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
            
    
    if len(components) == 0:
        components = lines         
        
    return components

def read_PDX_file(path, filename, encoding = 'UTF-8'):
    os.chdir(path)
    
    with open(filename, 'r', encoding = encoding) as f:
        lines = f.readlines()
        
    new_lines = []
    
    for line in lines:
        new_line = line.replace('    ','\t')
        new_lines.append(new_line)
    
    return read_PDX_file_subfunction(new_lines)

