import bpy, os, math, time, mathutils, sys, pickle, numpy as np

def generate_lights(bpy, params):
    object_name = params['object_name']
    # select all the old lights
    for o in bpy.data.objects:
        if o.type == 'LIGHT':
            o.select_set(True)
        else:
            o.select_set(False)
    # delete all the old lights
    bpy.ops.object.delete()
    # generate random xyz locations within range
    x_dim, y_dim, z_dim = 2, 2, 2
    # add each light
    for l in range(params['n_lights']):
        # create light datablock, set attributes
        light_data = bpy.data.lights.new(name="l_%d"%l, type='POINT')
        # set how bright this light is
        light_data.energy = params['light_energy']
        # create new object with our light datablock
        light_object = bpy.data.objects.new(name="l_%d"%l, object_data=light_data)
        # link light object
        bpy.context.collection.objects.link(light_object)
        # make it active
        bpy.context.view_layer.objects.active = light_object
        # generate random positions
        x_point = np.random.uniform(1, x_dim) * [1,1,-1][np.random.randint(3)]
        y_point = np.random.uniform(-y_dim, y_dim)
        z_point = np.random.uniform(-z_dim, z_dim)
        #change location
        light_object.location = (x_point,  y_point, z_point)
        # update scene, if needed
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()


def rotate_and_center_camera(bpy, position, params):
    """
    Focus the camera to a focus point and place the camera at a specific distance from that
    focus point. The camera stays in a direct line with the focus point.
    """
    camera = bpy.data.objects['Camera']
    # reposition camera
    camera.location = position
    # identify object center of mass
    object_center_of_mass = bpy.data.objects[params['object_name']].location
    # difference between location and origin
    looking_direction = camera.location - object_center_of_mass
    # unsure about details
    rot_quat = looking_direction.to_track_quat('Z', 'Y')
    # unsure about details
    camera.rotation_euler = rot_quat.to_euler()
    # define random-ish distance to object
    if params['jitter_distance']: 
        distance = params['distance'] + np.random.uniform(0, 2) 
        print('\n\n\n', distance)
    else: 
        distance = params['distance']
    # unsure about details
    camera.location = rot_quat @ mathutils.Vector((0, 0, distance))

def save_render(params, counts):
    """Save object as image or blend file"""
    #view_string = ['+%.02f'%i if i>=0 else '%.02f'%i for i in i_view ]
    #coordinates = '%sx_%sy_%sz'%(view_string[0], view_string[1], view_string[2])
    str_start = params['object_filename'].find('_') + 1
    str_end = params['object_filename'].find('.')
    object_name = params['object_filename'][str_start:str_end]
    print( '\n\n', object_name )
    name_to_save = '%s'%params['seed_label'] + '_' + object_name + '_view%02d'%(counts)
    filename_and_path = os.path.join(params['image_directory'], name_to_save)
    # unsure about details
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.resolution_percentage = params['resolution']
    bpy.context.scene.render.filepath=filename_and_path
    bpy.context.scene.render.engine= params['renderer'] #'BLENDER_EEVEE' # 'CYCLES'
    bpy.ops.render.render(write_still=True)

def load_object(bpy, params):
    # delete everything in the space  
    [bpy.data.collections.remove(i) for i in bpy.data.collections]
    [bpy.data.objects.remove(i) for i in bpy.data.objects]
    bpy.ops.object.delete()
    bpy.ops.object.camera_add()
    bpy.context.scene.camera = bpy.context.object
    path_to_object = os.path.join(params['object_directory'], params['object_filename'])
    with bpy.data.libraries.load(path_to_object) as (data_from, data_to):
        data_to.objects = [i for i in data_from.objects if i.lower() not in ['camera', 'light', 'point']]
    #Objects have to be linked to show up in a scene, assign color
    for _, obj in enumerate(data_to.objects):
        bpy.context.collection.objects.link(obj)
        if obj.hide_viewport:
            obj.hide_viewport = False
        obj.select_set(True)
    for ob in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = ob
    #align local and global coordinates
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    try:
        object_name = [i.name for i in bpy.data.objects if i.name[0:i.name.find('.')] in params['object_names']][0]
    except:
        object_name = [i.name for i in bpy.data.objects if i.name in params['object_names']][0]
    return object_name

def add_color(bpy, object_name, color='rgba', edit_toggle=True):
    """Adds color or texture to the object"""
    def create_material(bpy):
        id = bpy.data.materials.new("new")
        #diffuse
        #id.diffuse_shader = "OREN_NAYAR"
        id.diffuse_color = (.5, 0.5, .5, 1)
        #id.diffuse_intensity = 1
        id.roughness = 0.909
        # #specular
        # #id.specular_shader = "COOKTORR"
        id.specular_color = (0, 0, 0)
        # #id.specular_hardness = 10
        id.specular_intensity = 0.115
        return id
    clay_mat = create_material(bpy)
    for obj in bpy.context.scene.objects:
        if obj.type != 'LIGHT' and obj.type != 'CAMERA':
            obj.active_material = clay_mat

def set_background_and_size(params):
    # set window size to square
    bpy.context.scene.render.resolution_y = params['window_size']
    bpy.context.scene.render.resolution_x = params['window_size']
    # set background color to rgb+
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = params['background_color']
    bpy.context.scene.view_settings.view_transform = 'Standard'
    #bpy.context.scene.render.film_transparent = True

def generate_stimuli(bpy, params):
    set_background_and_size(params)
    params['object_name'] = load_object(bpy, params)
    add_color(bpy, params['object_name'])
    if params['observer'] == 'human': 
        radius = params['viewpoint_radius']
        n_points = 8
        angle = np.linspace( 0 , 2 * np.pi , n_points+1)
        x = np.repeat(params['distance'], len(angle))
        y = radius * np.cos( angle )
        z = radius * np.sin( angle )
        spherical_view = list( np.array([x, y, z]).T )[:-1]
        spherical_view = [spherical_view[i] for i in [1, 3, 6]]
    else: 
        radius = params['viewpoint_radius']
        n_points = 20 
        angle = np.linspace( 0 , 2 * np.pi , n_points+1)
        x = np.repeat(params['distance'], len(angle))
        y = radius * np.cos( angle )
        z = radius * np.sin( angle )
        spherical_view = list( np.array([x, y, z]).T )[:-1]
    counts = 0 
    
    rotations = [-45, 0, 45]
    count = 0 
    for i_view in spherical_view:
        
        i_rotation =  (math.radians(rotations[count]), 0, 0); count += 1
        bpy.data.objects[params['object_name']].rotation_euler = i_rotation

        # # generate random configuration of lights
        generate_lights(bpy, params)
        # rotate camera and reorient towards origin
        rotate_and_center_camera(bpy, i_view, params)
        # save this lighting x viewpoint image
        print('saving object_name', params['object_name'])
        save_render(params, counts); counts += 1

if __name__ == "__main__":
    
    ##### e.g. /Applications/Blender.app/Contents/MacOS/Blender -b -P generate_scene.py object_01.blend
    """$ blender -b -P generate_images.py"""





#    this_folder = os.path.split(os.getcwd())[1]
#    observer = sys.argv[-1]
#    print('observer', observer, this_folder ) 
#    if observer  == 'human': 
#        base_image_dir =  '/Users/biota/working/perirhinal_function/stimuli/images'
#        bg_color=(.03, .03, .03, 0) 
#    else: 
#        base_image_dir =  '/Users/biota/working/perirhinal_function/stimuli/model_stimuli'
#        bg_color=(0,0, 0, 1) 
#
#    base_object_dir =  '/Users/biota/working/perirhinal_function/stimuli/objects' 
#
#    params = {'window_size': 256,
#              'object_directory': os.path.join(base_object_dir, this_folder),
#              'image_directory':  os.path.join(base_image_dir, this_folder), 



    this_folder = os.path.split(os.getcwd())[0]
    observer = sys.argv[-1]

    print( 'generate_images', observer )
    print('observer', observer, this_folder )
    if observer  == 'human':
        image_directory =  os.path.join(this_folder, 'images')
        bg_color=(.03, .03, .03, 0)
    else:
        image_directory  = os.path_join(this_folder, 'model_images')
        bg_color=(0,0, 0, 1)

    object_directory  = os.path.join(this_folder, 'objects')

    params = {'window_size': 256,
              'object_directory': object_directory,
              'image_directory':  image_directory,
              'background_color': bg_color, 
              'object_names': ['Cube', 'Sphere', 'Cylinder', 'Generated Shape', 'my_shape'],
              'light_scale': 1,
              'light_energy': 20,
              'n_lights': 20,
              'resolution': 200,
              'distance': 3.5,
              'viewpoint_radius':2,
              'jitter_distance':2,
              'renderer': 'BLENDER_EEVEE', # 'CYCLES'
              'observer': observer, 
             }
   
    #if not os.path.isdir(params['image_directory']):
    #    print( '~~~~', params['image_directory']) 
    #    os.mkdir(params['image_directory'])

    blender_objects = [i for i in os.listdir(params['object_directory']) if i != '.DS_Store']
    blender_objects = [i for i in blender_objects if ('blend1' not in i) * ('blend' in i)]
         
    with open(os.path.join(params['object_directory'], 'metadata.pickle'), 'rb') as handle:
        metadata = pickle.load(handle)
    
    for i_object in np.sort(blender_objects):
       
        print( '\n\n', i_object )
        object_tag = i_object[:i_object.find('.')]
        print( object_tag) 
        params['object_filename'] = i_object
        params['seed_label'] = i_object[:3] #metadata[i_objrv]['big_shapeseed']
        generate_stimuli(bpy, params)
