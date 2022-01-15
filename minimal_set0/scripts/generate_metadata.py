import os, model_estimate, json, pickle, numpy as np

def format_metadata(base_path, this_folder):

    path_to_stimuli      = os.path.join(base_path , 'images')
    path_to_metadata     = os.path.join(base_path, 'objects')
    metadata_files       = [i for i in os.listdir(path_to_metadata) if 'meta' in i]

    stim_info = {}

    files                = [i for i in os.listdir(path_to_stimuli) if i != '.DS_Store']
    object_names         = np.unique( [i[0:i.find('view')-1] for i in files] )
    stim_info['images']  = {i:list(np.sort([o for o in files if i in o])) for i in object_names}
    stim_info['objects'] = list( object_names )

    stim_info['pairs']   = {'surface':{}, 
                            'structure':{}, 
                            'configuration':{}
                            }  

    for obj in stim_info['objects']:

        # select objects within the same set (i.e. same initial random seed)
        same_set = [i for i in object_names if (i!=obj) * (i[0:3]==obj[0:3])]

        # select the same objects that have with a different surface
        diff_surface = [i for i in same_set if (i[4]!=obj[4])*(i[5:]==obj[5:])]

        # identify all objects within the same surface...
        same_surface = [i for i in same_set if (i[4]==obj[4])]
        
        #diff_surface = [i for i in object_names if (i[0:3]==obj[0:3])*(i[4:]==obj[4:])]
        # identigy all objects with a different structure
        diff_structure = [i for i in same_surface if (i[5]!=obj[5])*(i[6]==obj[6])]
        # identify all objects with a different configuration
        diff_configuration = [i for i in same_surface if (i[:6]==obj[:6])*(i[6]!=obj[6])]

        stim_info['pairs']['surface'][obj] = diff_surface
        stim_info['pairs']['structure'][obj] = diff_structure
        stim_info['pairs']['configuration'][obj] = diff_configuration

    stim_info['metadata'] = {}

    metadata_files = [i for i in os.listdir(path_to_metadata) if 'meta' in i]
    
    for i_file in metadata_files:
        with open(os.path.join(path_to_metadata, i_file), 'rb') as handle:
            i_metadata = pickle.load(handle)
            for i_obj in i_metadata:
                serialized_data = {i: str(i_metadata[i_obj][i]) for i in i_metadata[i_obj]}
                stim_info['metadata'][i_obj] = serialized_data

    stim_info['model_distance'] = model_estimate.pairwise_similarities(path_to_stimuli)

    return stim_info

def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + content)


if __name__ == '__main__':

    this_folder = os.path.split(os.getcwd())[1]
    base_path = '/Users/biota/working/perirhinal_function/stimuli/'
    json_filename = 'stimulus_information'

    # generate metadata for set of stimuli in this directory
    set_metadata = format_metadata(base_path, this_folder)

    # # save metadata as json
    with open('%s.json'%json_filename, 'w') as json_file:
        json.dump(set_metadata, json_file)

    # change to made it easier to load as a variable in javascript
    line_prepender('%s.json'%json_filename, 'stimulus_info = ')
