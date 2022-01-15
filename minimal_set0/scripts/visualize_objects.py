import os, pickle, bpy, numpy as np
from mathutils import Vector

def scale_and_center_object(xyz=(0,0,0)):
    """
    thanks to:
    https://blender.stackexchange.com/questions/137485/how-to-scale-primitive-shapes-in-blender-so-that-they-are-within-a-unit-sphere
    """
    def bbox(ob):
        return (Vector(b) for b in ob.bound_box)
    def bbox_center(ob):
        return sum(bbox(ob), Vector()) / 8
    def mesh_radius(ob):
        o = bbox_center(ob)
        return max((v.co - o).length for v in ob.data.vertices)

    object = bpy.context.selected_objects[0]
    scale_factor = 1 / mesh_radius(object)
    object.scale *= scale_factor
    obj = bpy.context.active_object
    obj.location = (xyz[0],xyz[1],xyz[2])

def delete_everything():
    [bpy.data.collections.remove(i) for i in bpy.data.collections]
    [bpy.data.objects.remove(i) for i in bpy.data.objects]
    #[bpy.data.worlds.remove(i) for i in bpy.data.worlds]
    
def generate_and_scale_object(bpy, i_params):
    """
    seed, n_subdivisions, n_extrusions, n_bigshapes, n_medshapes, nlocseeds, nshapeseeds
    """

    bpy.ops.mesh.shape_generator(
        random_seed=i_params['seed'],
        mirror_x=0,
        mirror_y=0,
        mirror_z=0,
        favour_vec=i_params['axis_preferences'],
        amount=i_params['n_extrusions'],
        is_subsurf=(i_params['n_subdivisions']>0),
        subsurf_subdivisions=i_params['n_subdivisions'],
        big_shape_num=i_params['n_bigshapes'],
        medium_shape_num=i_params['n_medshapes'],
        medium_random_scatter_seed=i_params['med_locseed'],
        big_random_scatter_seed=i_params['big_locseed'],
        big_random_seed=i_params['big_shapeseed'],
        medium_random_seed=i_params['med_shapeseed'],
        )
    
    bpy.ops.object.join()
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')
    bpy.ops.object.location_clear(clear_delta=False)
    # save a single object scaled and located at the origin
    scale_and_center_object()
    
#if use_preset_seeds:
#    seeds = [411, 432, 40, 4491, 76, 9016, 3828, 2284, 4471, 4510, 5327, 9459, 4278, 5214, 7650, 8820] #6246
#else:
#    seeds =  np.random.randint(0, 10000, 1)
#[6246] # 5525 # our fav? 5525




if __name__ == '__main__':
    """
    usage:
        $ /Applications/Blender.app/Contents/MacOS/Blender -b -P generate_object.py
    """
    
#    stimulus_set = {
#        'location': '/Users/biota/working/perirhinal_function/stimuli/human/pilot1/objects/',
#        'save_string': 'seed%d_%d%d%d%d',
#        'axis_preferences':[1,  1, 1],
#        'n_bigshapes': 3,
#        'n_medshapes': 2,
#        'big_shapeseed':3563546,
#        'big_locseeds': [0, 12], 
#        
#        'med_locseeds': [0, 2], #7
#        'med_shapeseeds': [1, 3], 
#        'n_extrusions': 3,
#        'seed':333, 
#        'range_subdivisions': [0, 1, 5],
#        }
        
        
    seeds = [{
        'axis_preferences':[.4, 1, 1],
        'n_bigshapes': 3,
        'n_medshapes': 1,
        'big_shapeseed': 8,
        'big_locseeds': [10,11],
        'med_locseeds': [7, 11],
        'med_shapeseeds': [5, 8],
        'n_extrusions': 2,
        'seed':0,
        'range_subdivisions': [0, 1, 5]},
        
        {'axis_preferences':[.1, 1, 1],
        'n_bigshapes': 2,
        'n_medshapes': 0,
        'big_shapeseed':532,
        'big_locseeds': [0, 4],
        'med_locseeds': [0, 2], #7
        'med_shapeseeds': [0, 1],
        'n_extrusions': 3,
        'seed':0,
        'range_subdivisions': [0,]}]
        
    
    stimulus_set = seeds[1]
    save_objects = 0 
    stimulus_key = {} 
    ignore = ['location', 'save_string', 'range_subdivisions', 'big_locseeds', 
              'med_locseeds', 'big_shapeseeds', 'med_shapeseeds']
              
    delete_everything()

    sdcount = 0 
    for stimulus_set['n_subdivisions'] in stimulus_set['range_subdivisions']:
        
        blcount = 0 
        for stimulus_set['big_locseed'] in stimulus_set['big_locseeds']:
            
            mlcount = 0 
            for stimulus_set['med_locseed'] in stimulus_set['med_locseeds']:
                
                mscount = 0 
                for stimulus_set['med_shapeseed'] in stimulus_set['med_shapeseeds']:
                    
                    generate_and_scale_object(bpy, stimulus_set)                    
                    obj = bpy.context.active_object
                    obj.location = (blcount*3, mlcount*3, mscount*3 + sdcount*6)
                    
                    mscount += 1
                mlcount += 1
            blcount += 1         
        sdcount += 1