#### Scripts to generate blender objects + multiple images of those objects 

After creating the conda environment specified in `environment.yaml` running the code

$ source activate mtl_perception

$ cd minimal_set0/scripts/

$ python generate_stimulus_set.py human

should create a small set of objects in `minimal_set0/objects/` and, from those, a set of images in `minimal_set0/images/`. This will also create  covariance matrix that visualizes the between-object correlation (across images) in `minimal_set0/scripts/covariance_matrix.pdf`

