######################################################################################################################################
#   _    _  _____   ____            _        _            
#  | |  | |/ ____| |  _ \          | |      | |           
#  | |  | | |      | |_) | ___ _ __| | _____| | ___ _   _ 
#  | |  | | |      |  _ < / _ \ '__| |/ / _ \ |/ _ \ | | |
#  | |__| | |____  | |_) |  __/ |  |   <  __/ |  __/ |_| |
#   \____/ \_____| |____/ \___|_|  |_|\_\___|_|\___|\__, |  
#                                      @ Jagust Lab  __/ |
#                                             -TJW  |___/  
#  Hello and welcome to easy PCA!
#    
#  This application accepts a path of nifti images and will run PCA on them! Can be any modality but must be 3D. 
#  
#  Pre-reqs: 
#      1.) Register your images to a template. All must be in the same space! This is tested in MNI152.
#      2.) Intensity normalize your data. This application will not i-norm you images, processing must be uniform across images.
#      3.) Images must be readable by Nibabel (nifti's are good)
#      4.) Calculate required ram for the number of images you will be loading
#      5.) Have fun! :)
#  
#  Output:
#      1.) 3D principal components as compressed nifti images.
#      2.) Spreadsheets including the eigenvectors and eigenvalues 
#  
#  Method citations (not mine):
#      https://doi.org/10.2967%2Fjnumed.118.207811
#      http://dx.doi.org/10.1007/978-3-540-85988-8_53
#
#  To use this for train / test validation, see the paper below.
#     https://doi.org/10.1212/WNL.0b013e31829e6f94 
# 
#  Created by Tyler J. Ward
######################################################################################################################################
