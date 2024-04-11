import os

file_dir = os.getcwd()

base_path = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\src'
interface_path = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\src\interface'   
event_modifiers_path = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\src\common\event_modifiers'
gfx_interface_path = r'C:\Users\idria\Documents\Paradox Interactive\Europa Universalis IV\mod\src\gfx\interface'
output_file = 'output.csv'

#%% .gui files functions.
def scan_gui_file(file_name, sprite_set):
    with open(file_name, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        
    for line in lines:        
        if 'spriteType' in line:
            sprite_string = line.split('"')[1].split('"')[0]
            sprite_set.add(sprite_string)
            
    return sprite_set

def scan_folder_for_gui(sprite_set):
    files = os.listdir()
    
    for file in files:
        if file[-4:] == '.gui':
            sprite_set = scan_gui_file(file, sprite_set)
            
        elif file[-4:] != '.gfx':
            try:
                os.chdir(file)
                sprite_set = scan_folder_for_gui(sprite_set)
                os.chdir('..')
                
            except:
                pass
    
    return sprite_set

#%% event modifiers function
def scan_event_modifiers(sprite_set):
    files = os.listdir()
    
    for file_name in files:
        with open(file_name, 'r', encoding = 'utf-8') as f:
            lines = f.readlines()
            
        for line in lines:        
            if 'picture' in line:
                try:
                    sprite_string = line.split('"')[1].split('"')[0]
                    sprite_set.add(sprite_string)
                except:
                    # Backup, might not be entirely accurate.
                    sprite_string = line.split('=')[1].replace(' ','').replace('\t','').replace('\n','')
                    sprite_set.add(sprite_string)
        
    return sprite_set

#%% missions function
def scan_missions(sprite_set):
    files = os.listdir()
    
    for file_name in files:
        with open(file_name, 'r', encoding = 'ANSI') as f:
            lines = f.readlines()
            
        for line in lines:        
            if 'icon =' in line:
                sprite_string = line.split('=')[1].replace(' ','').replace('\t','').replace('\n','')
                sprite_set.add(sprite_string)
                
    return sprite_set

#%% look through loc
def scan_loc(sprite_set):
    files = os.listdir()
    
    for file_name in files:
        with open(file_name, 'r', encoding = 'UTF-8') as f:
            lines = f.readlines()
            
        for line in lines:        
            if ':0 "£' in line:
                sprite_string = line.split('"£')[1].split('£"')[0]
                sprite_set.add(sprite_string)
                
    return sprite_set

#%% .gfx file functions
def scan_gfx_file(file_name, dds_set, sprite_set):    
    with open(file_name, 'r', encoding = 'utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):        
        if '.dds"' in line:
            decrement = 1
            while 'name' not in lines[i-decrement]:
                decrement += 1
                
            sprite_name = lines[i-decrement].split('"')[1].split('"')[0]
            if sprite_name not in sprite_set:
                pass
                # print(sprite_name)
            
            dds_string = line.split('"')[1].split('"')[0]
            dds_set.add(dds_string)
            
            
    return dds_set

def scan_folder_for_gfx(dds_set, sprite_set):
    files = os.listdir()
    
    for file in files:
        if file[-4:] == '.gfx':
            dds_set = scan_gfx_file(file, dds_set, sprite_set)
            
        elif file[-4:] != '.gui':
            try:
                os.chdir(file)
                dds_set = scan_folder_for_gfx(dds_set, sprite_set)
                os.chdir('..')
                
            except:
                pass
    
    return dds_set

# Runs through gfx/interface
def check_folder_for_gfx(dds_set, sprite_set, surplus, prefix):
    if prefix in ['/advisors/', '/dwarovar_dungeons/', '/institutions/']:
        return surplus

    files = os.listdir()
        
    for file in files:
        if prefix == '/ideas_EU4/':
            if ('_influence' in file) or ('_loyalty_modifier.dds' in file) or ('_loyalty_modifier_opposite.dds' in file):
                continue
            

        if file[-4:] == '.dds':
            file_string = prefix + file
            if file_string[0] == '/':
                file_string = file_string[1:]
                
            if (file_string not in dds_set) and (file not in dds_set) and (file.replace('.dds','') not in sprite_set):
                surplus.append(file_string)
                
        else:
            try:
                os.chdir(file)
                surplus = check_folder_for_gfx(dds_set, sprite_set, surplus, f'{prefix}/{file}/')
                os.chdir('..')
            except:
                pass

    return surplus

                
#%% Main function
def main():    
    sprite_set = set()
    os.chdir(interface_path)
    sprite_set = scan_folder_for_gui(sprite_set)
    
    os.chdir(event_modifiers_path)
    sprite_set = scan_event_modifiers(sprite_set)

    os.chdir('..')
    os.chdir('province_triggered_modifiers')
    sprite_set = scan_event_modifiers(sprite_set)

    os.chdir(base_path)
    os.chdir('missions')
    sprite_set = scan_missions(sprite_set)
    
    os.chdir('..')
    os.chdir('localisation')
    sprite_set = scan_loc(sprite_set)
    
    dds_set = set()
    
    os.chdir(interface_path)
    scan_folder_for_gfx(dds_set, sprite_set)
    
    dds_set = [item.replace("\\","/").replace("//","/") for item in dds_set]
    dds_set = [item.replace("gfx/interface/","") for item in dds_set if "gfx/interface" in item]
        
    os.chdir(gfx_interface_path)
    
    surplus = []
    surplus = check_folder_for_gfx(dds_set, sprite_set, surplus, "")
    
    os.chdir(file_dir)
    
    with open(output_file, 'w', encoding = 'utf-8') as f:
        for item in surplus:
            path = gfx_interface_path+'/'+item
            byte_size = os.stat(path).st_size
            f.write(f'{byte_size / 1000}, {item}\n')
    
   
    return sprite_set, dds_set
    
sprite_set, dds_set = main()