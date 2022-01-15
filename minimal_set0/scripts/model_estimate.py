import os, numpy as np 
from PIL import Image
from torchvision import transforms
import torchvision.models as models
import torch, torch.nn as nn
import matplotlib.pylab as plt

def define_model_and_preprocessing():
    
    model = nn.Sequential(*list(models.resnet18(pretrained=True).children())[:-2])

    preprocess = transforms.Compose([
        transforms.Resize(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    
    return model, preprocess 
    
def extract_model_responses(model, preprocess, info): 

    representations = {}

    for i_file in info['image_files']:

        filename = os.path.join(info['path_to_stimuli'], i_file)
        input_image = Image.fromarray(np.array(Image.open(filename))[:,:,:3])
        input_tensor = preprocess(input_image).unsqueeze(0)

        with torch.no_grad():
            representations[i_file] = np.array(model(input_tensor).detach().flatten())

    return representations
    
def determine_similarities(patterns, info):
    
    objects = np.unique( [i[:i.find('_view')] for i in info['image_files'] ])
    print( objects ) 
    pairwise = {}
    for iobj in objects: 
        pairwise[iobj] = {} 
        for jobj in [o for o in objects if o!=iobj]:
            ij = [np.mean([patterns[img] for img in patterns if obj in img],0) for obj in [iobj, jobj]]
            pairwise[iobj][jobj] = np.corrcoef(ij)[0, 1]
   
    return pairwise

def save_covariance_matrix(patterns, info): 
    
    objects = np.unique( [i[:i.find('_view')] for i in info['image_files'] ])

    # generate covariance matrix
    avg_objects = [np.mean([patterns[i] for i in patterns if O in i],0) for O in objects]
    item_covariance = np.corrcoef( avg_objects )
    # save covariance matrix
    plt.imshow(item_covariance, cmap='plasma')
    plt.xticks(range(len(objects)), objects,rotation=90, fontsize=4);
    plt.yticks(range(len(objects)), objects,  fontsize=4);
    plt.ylim(len(objects)-.5, -.5, )
    plt.title('pairwise correlation between objects', fontsize=10, y=1.05)
    plt.colorbar()
    plt.savefig('covariance_matrix.pdf')
 
def pairwise_similarities(path): 
    print('\n\n\nestimating model-based similarity between objects\n\n\n')     
    stim_info = {'path_to_stimuli': path, 
                 'image_files': [i for i in os.listdir(path) if 'png' in i]}
    
    # define model and proprocessing steps to take over images 
    model, preprocess = define_model_and_preprocessing()
    # extract model representations from an IT-like layer
    representations = extract_model_responses(model, preprocess, stim_info)
    # determine the pairwise relationships for trial-by-trial storage late
    pairwise_relationships = determine_similarities(representations, stim_info)
    # generate a figure of the covariance between objects (averaged over images) 
    save_covariance_matrix(representations, stim_info)

    return pairwise_relationships 

if __name__ == '__main__': 
    #this_folder = os.path.split(os.getcwd())[1] 
    #image_folder = os.path.join('/Users/biota/working/perirhinal_function/stimuli/images', this_folder) 
    pairwise_similarities( os.path.join( os.path.split(os.getcwd())[0], 'images') ) 

