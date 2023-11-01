import numpy as np
import re
import os
from datetime import datetime
import matplotlib.pyplot as plt
from zipfile import ZipFile

from classes import Province, Country, Superregion

#%% Unzipping compressed saves, renaming gamestate. This needs to be fun before running the code chunks below.

# zip_path = r'C:\Users\idria\Documents\Programming\EU4\saves\zip_files'

def unzip_saves(zip_path):
    os.chdir(zip_path)
    
    files = os.listdir()
    for file in files:
        print(file)
        with ZipFile(file) as zObject:
            zObject.extractall()
            
        with open(r'meta', 'r', encoding = 'ANSI') as f:
            mp = ''
            date = ''
            country_name = ''
            lines = f.readlines()
            for line in lines:
                if 'date=' in line:
                    date = line.split('=')[1].replace('.','_').strip('\n')
                if 'multi_player=yes' in line:
                    mp = 'mp_'
                if 'displayed_country_name' in line:
                    country_name = line.split('=')[1].strip('\n').strip('"').replace(' ','_')
                
        save_name = mp + country_name + date
        
        if save_name != '':
            os.rename('gamestate', save_name)
        else:
            os.remove('gamestate')
        
        os.remove('meta')
        os.remove('ai')
        os.remove(file)


#%% Savegame stuff.
# Thorfindel request.
# Entire file needs to be run first to get continent stuff to work properly.
from scipy.optimize import curve_fit

def check_for_owner_changes(filename, encoding = 'ANSI'):
    print(filename)
    search_line = '\t\t\t\towner='
    
    
    superregions = {}
    
    year = re.sub("[^0-9]", "", filename)
    year = year[:4]
    
    for superregion in Superregion.class_dict:
        superregions[superregion] = []
    
    with open(filename, 'r', encoding = encoding) as f:
        lines = f.readlines()
                
        prov_num = 0
        
        for i, line in enumerate(lines):
            if line[0] == '-' and line[-3:] == '={\n':
                prov_num = int(line[1:-3])
            
            if search_line in line:
                above_line = lines[i-1]
                if '1444' not in above_line:
                    owner_change_year = above_line.split('.')[0].strip('\t')
                    try:
                        superregion = str(Province.class_dict[prov_num].superregion)
                        superregions[superregion].append(owner_change_year)
                    except:
                        print(i, prov_num)
    
    active_regions = ''
    sum_owner_changes = 0

    for superregion in superregions:
        if superregion != []:
            active_regions += superregion.replace('_superregion','') + ' '
            sum_owner_changes += len(superregions[superregion])            
    
    average_yearly_changes = sum_owner_changes / (int(year) - 1444)
    
    print('')
    
    return year, sum_owner_changes, average_yearly_changes, active_regions

def get_prov_changes_in_save(filename, encoding = 'ANSI'):
    print(filename)
    search_line = '\t\t\t\towner='
        
    prov_changes = [[datetime.strptime('1000.1.1', "%Y.%m.%d"), 0, '---']]
    
    with open(filename, 'r', encoding = encoding) as f:
        lines = f.readlines()
                
        prov_num = 0
        
        for i, line in enumerate(lines):
            if line[0] == '-' and line[-3:] == '={\n':
                prov_num = int(line[1:-3])
            
            if search_line in line:
                date = lines[i-1].split('=')[0].replace('\t','')
                if int(date.split('.')[0]) > 1443:
                    if date != '1444.11.12':
                        datetime_obj = datetime.strptime(date, "%Y.%m.%d")
                        owner_new = line[-5:-2]
                        
                        ownership_change = [datetime_obj, Province.class_dict[prov_num], owner_new]
                        prov_changes = np.vstack((prov_changes, ownership_change))
    
    prov_changes = prov_changes[1:]
    
    return prov_changes[prov_changes[:, 0].argsort()]

def count_living_tags():
    living_tags = 0
    for country in Country.instances:
        if country.provinces != []:
            living_tags += 1
        
    return living_tags

def get_yearly_living_tags(filename, count_1444_11_12 = False, path = r'C:\Users\idria\Documents\Programming\EU4\saves\saves_to_check'):
    os.chdir(path)
    current_year = 1444
    
    years = [1444]
    
    prov_changes = get_prov_changes_in_save(filename)
    
    prov_changes_history = []
    
    cumulative_prov_changes = 0
    
    living_tags_history = []
    
    for prov_change in prov_changes:
        province = prov_change[1]
        new_owner_tag = prov_change[2]
        cumulative_prov_changes += 1

        if prov_change[0].year != current_year or count_1444_11_12:
            current_year = prov_change[0].year
            years.append(current_year)
            living_tags_history.append(count_living_tags())
            prov_changes_history.append(cumulative_prov_changes)
            
        province.change_ownership(new_owner_tag)
    
    return years[:-1], living_tags_history, prov_changes_history

def run_Thorfindel_request_2():
    # Amount of living tags per year.
    path = r'C:\Users\idria\Documents\Programming\EU4\saves\saves_to_check'
    os.chdir(path)
    files = os.listdir()
    
    years_storage = []
    living_tags_storage = []
    cumulative_prov_changes_storage = []
    
    f, ax = plt.subplots(1)
    plt.grid()
    plt.title('Living tags per year', fontsize = 48)
    plt.ylabel('Tags alive', fontsize = 40)
    plt.xlabel('Year', fontsize = 40)
    for file in files:
        years, living_tags_history, cumulative_prov_changes = get_yearly_living_tags(file)
        ax.plot(years[-1], living_tags_history[-1],'k.', markersize = 12)
        ax.plot(years, living_tags_history,'-.')
        
        years_storage.append(years)
        living_tags_storage.append(living_tags_history)
        cumulative_prov_changes_storage.append(cumulative_prov_changes)
        
        for country in Country.instances:
            country.provinces = []
        
        for province in Province.instances:
            province.owner = province.owner_original
            if province.owner != 'None':
                province.owner.provinces.append(province)
    
    return years_storage, living_tags_storage, cumulative_prov_changes_storage

def prov_changes_analysis(years_storage, cumulative_prov_changes_storage, subtract_1444 = True, max_1444_changes = 100):
    f, ax = plt.subplots(1)
    plt.grid()
    plt.title('Cumulative prov changes per year', fontsize = 48)
    plt.ylabel('Total prov changes', fontsize = 40)
    plt.xlabel('Years since start', fontsize = 40)
    for years, cumulative_prov_changes in zip(years_storage, cumulative_prov_changes_storage):
        if cumulative_prov_changes[0] < max_1444_changes:
            if subtract_1444:
                cumulative_prov_changes = [x - cumulative_prov_changes[0] for x in cumulative_prov_changes]
                
            years = [year - 1444 for year in years]
                
            ax.plot(years[-1], cumulative_prov_changes[-1],'k.', markersize = 12)
            ax.plot(years, cumulative_prov_changes, '-')

def living_tag_analysis(years_storage, living_tags_storage, cutoff = 500):
    
    years_analysis = []
    living_tags_analysis = []

    for years, living_tags in zip(years_storage, living_tags_storage):
        if living_tags[0] > 700:
            years_analysis.append(years)
            living_tags_analysis.append(living_tags)

    x = np.concatenate(years_analysis, axis = 0)
    y = np.concatenate(living_tags_analysis, axis = 0)
    
    xp = np.linspace(1444, 1822, 1822-1444, endpoint = False)
                
    # Exponential function.
    x -= 1444
    xp -= 1444
    
    y = y[x <= cutoff]
    x = x[x <= cutoff]
    xp = xp[xp <= cutoff]

    p0 = [350, -0.0059937829994006295, 350]    
    
    popt, pcov = curve_fit(lambda t, a, b, c: a * np.exp(b * t) + c, x, y, maxfev=5000, p0 = p0)
    
    a = popt[0]
    b = popt[1]
    c = popt[2]
    
    y_fitted = a * np.exp(b * xp) + c
    
    ax = plt.axes()
    ax.scatter(x, y, label='Raw data')
    ax.plot(xp, y_fitted, 'k', label='Fitted curve')
    ax.set_title(r'Tags alive per year, modelled as exponential decay', fontsize = 48)
    ax.plot(xp, [c]*len(xp), 'k--', label = 'Offset')
    ax.set_ylabel('Total tags alive', fontsize = 40)
    ax.set_xlabel('Years since start', fontsize = 40)
    ax.legend(fontsize = 32)
    
    return popt



def run_Thorfindel_request():
    path = r'C:\Users\idria\Documents\Programming\EU4\saves\saves_to_check'
    os.chdir(path)
    
    files = os.listdir()
    
    years = []
    changes = []
    yearly_changes = []
    active_regions = []
    
    for file in files:
        year, change, yearly_change, active_region = check_for_owner_changes(file)
        years.append(year)
        changes.append(change)
        yearly_changes.append(yearly_change)
        active_regions.append(active_region)
        
    return years, changes, yearly_changes, active_regions
    
