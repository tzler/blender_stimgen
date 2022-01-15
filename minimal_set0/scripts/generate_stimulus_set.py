import os, sys

if __name__ == '__main__': 
    
    generate_objects, generate_images, generate_metadata, model_covariance, move_to_server = 1, 1, 1, 1, 0
    
    this_folder = os.path.split(os.getcwd())[0]
    
    command = sys.argv[-1] 

    if command not in ['human', 'model']:
        print('specify model or human to determine which kind of stimuli to generate') 
        exit() 

    if command == 'model': 
        image_directory = os.path.join(this_folder, 'model_images')
    elif command == 'human':  
         image_directory = os.path.join(this_folder, 'images')

    object_directory = os.path.join(this_folder, 'objects')

    if generate_objects:
        # remove objects and images from previous iterations, if they exist
        if not os.path.exists(object_directory):
            os.makedirs(object_directory)
            print('creating object directory', object_directory) 
        else: 
            print('using old object directoy') 
            os.system('rm %s/*'%object_directory)
            print('clearing out old files with rm %s/*'%object_directory)

        os.system('/Applications/Blender.app/Contents/MacOS/Blender -b -P generate_objects.py') 
    
    if generate_images: 
        # remove objects and images from previous iterations, if they exist
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)
            print('creating image directory', image_directory) 
        else: 
            print('using old image directoy') 
            os.system('rm %s/*'%image_directory)
            print('running: rm %s/*'%image_directory)

        os.system('/Applications/Blender.app/Contents/MacOS/Blender -b -P generate_images.py %s'%command) 
    
    if generate_metadata: 
         os.system('python generate_metadata.py') 
   
    if model_covariance: 
        os.system('python model_estimate.py')
    
    #if move_to_server: 
        #server_image_location = '/home/tyler/online_experiments/pilots/samediff_scratch/images'
        #server_metadata_location = '/home/tyler/online_experiments/pilots/samediff_scratch/'
        #os.system('scp %s/* tyler@stanfordmemorylab.com:%s'%(image_directory, server_image_location))
        #os.system('scp stimulus_information.json tyler@stanfordmemorylab.com:%s'%(server_metadata_location))
