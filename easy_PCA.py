#!/usr/bin/env python3

descript_text = '''
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
######################################################################################################################################'''

# Argument parser
import argparse
print(descript_text)
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--datapath",type=str, help="Directory where the images are located", required=True)
parser.add_argument("-o", "--outpath",type=str, help="Where to save PC's",default='', required=False)
parser.add_argument("--eigencutoff",type=float, help="Percent 0-1 cutoff for eigenvalues",default=0.005, required=False)
parser.add_argument("--template",type=str, help="Template for reslicing images. should be same space is images. Can be one of your images. Optional.",default='', required=False)
parser.add_argument("--mask",type=str, help="Mask PET images by this... mask. Optional.",default=False, required=False)
parser.add_argument("--smooth",nargs=3,type=int, help="Smooth images by FWHM (pyspmsmooth) [X Y Z]. Default == [8 8 8]",default=[4,4,4] ,required=False)

args = parser.parse_args()
if args.outpath == '':
    args.outpath = args.datapath

import numpy as np
args.smooth = np.asarray(args.smooth)


# Libraries for PCA
import os
import subprocess
from memory_profiler import profile

import nibabel as nib
import glob
import pandas as pd
import re

from nilearn.image import resample_to_img
from nilearn.image import resample_img
from nibabel.processing import resample_to_output

import importlib.util
spec = importlib.util.spec_from_file_location("spm_smooth", '/home/jagust/adni/pipeline_scripts/python_scripts/smoothing.py')
smo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smo)

# Global definitions

SUPPORTED_EXTENSIONS = [  
                      '*.nii',
                      '*.nii.gz',
                      ]
# Functions:
def main():
    Easy_PCA()
    print('Done!')

def all_equal(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)

@profile
def load_data(IMAGES,template):
    print('\nLoading and preprocessing images...')
    fourD = False
    img_affines = nib.load(IMAGES[0]).affine
    if args.mask:
        mask_img = nib.load(args.mask)
        if ~((mask_img.affine == img_affines).all()):
            print('Reslicing the mask img')
            mask_img = resample_to_img(mask_img,template,interpolation='nearest')
        mask_img = mask_img.get_fdata() == 0
    for path in IMAGES:
        print('  '+path)
        img = nib.load(path)
        img_array = img.get_fdata().copy()
        if args.mask:img_array[mask] = 0 # or np.nan if you want to use edge_pres(erving)
        img = nib.Nifti1Image(img_array,affine=img.affine.copy(),header=img.header.copy())
        if (args.smooth != 0).any():
            img = smo.spm_smooth(img,s=args.smooth,edge_pres=False)
        if args.template != '':
            img = resample_to_img(img,template)
        img_array = img.get_fdata()
        img_array = np.nan_to_num(img_array)
        if args.mask: img_array[mask_img] = 0
        if type(fourD) == bool:
            fourD = img_array.reshape(template.shape + (1,))
        else:
            fourD = np.concatenate((fourD, img_array.reshape(template.shape + (1,))), axis=3)
    summed_img = np.nansum(fourD,axis=-1)
    meanImg = summed_img/len(IMAGES)
    return meanImg,fourD

@profile
def Easy_PCA():
    '''
    This method requires equal image dimensions so you need a template to reslice your data to. 
    '''
    IMAGES = get_data(args.datapath)
    if args.template == '':
        template = nib.load(IMAGES[0])
    else:
        template = nib.load(args.template)
    
    meanImg,fourD = load_data(IMAGES,template)
    meanImg_img = nib.Nifti1Image(meanImg.copy(),affine=template.affine.copy(),header=template.header.copy())
    meanImg_img.to_filename(os.path.join(args.outpath,'mean_img.nii.gz'))

    D = fourD - (meanImg.reshape(template.shape + (1,))@ np.ones((1,len(IMAGES))))
    Dprime = np.transpose(D, [3,0,1,2]) # same as Dprime=np.einsum('bcda', D)
    Dc=np.einsum('nabc,abcN->nN', Dprime,D) * (1/(len(IMAGES)-1))
    # same as this: Dc = np.tensordot(D.reshape(((256**3),8)),D.reshape(((256**3),8)).T, axes = ((0),(-1))) * (1/(asubs-1)) 
    P, d, Q = np.linalg.svd(Dc, full_matrices=False)#full_matrices=False
    print('P',P.shape)
    print('d',d.shape)
    print('Q',Q.shape)
    sum_of_eigenvalues = np.nansum(d)
    print("Saving PC's:")
    for i in range(len(d)):
        eigen_strength = d[i] / sum_of_eigenvalues
        if eigen_strength < args.eigencutoff:
            break
        mask_img = nib.Nifti1Image(D@P[:,i],affine=template.affine,header=template.header)
        output_filepath = os.path.join(args.outpath,f'PC{i}_{eigen_strength:0.4f}.nii.gz')
        print('  '+output_filepath)
        if ask_to_overwrite(output_filepath) == True:
            mask_img.to_filename(output_filepath)
    d_percent = d/sum_of_eigenvalues
    df = pd.DataFrame()
    df['PC'] = np.arange(1,len(d_percent)+1)
    df['Eigenvalue percent'] = d_percent
    df['Eigenvalue'] = d
    print('Saving eigenvalues...')
    df_outpath = os.path.join(args.outpath,f'PCA_eigenvalues.csv')
    if ask_to_overwrite(df_outpath) == True:
        df.to_csv(df_outpath,index=False)
    print('Saving eigenvectors...')
    df = pd.DataFrame()
    df['Image'] = IMAGES
    for i,vec in enumerate(P):
        df[f'Eigenvector ({i})'] = vec
    df_outpath = os.path.join(args.outpath,f'PCA_eigenvectors.csv')
    if ask_to_overwrite(df_outpath) == True:
        df.to_csv(df_outpath,index=False)

def ask_to_overwrite(filepath):
    """Produces a prompt asking about overwriting a file.

    # Arguments
        filepath: the path to the file to be overwritten.

    # Returns
        True if we can proceed with overwrite, False otherwise.
    """
    if not os.path.exists(filepath):
        return True
    get_input = input
    overwrite = get_input('[WARNING] %s already exists - overwrite? '
                          '[y/n]' % (filepath))
    while overwrite not in ['y', 'n']:
        overwrite = get_input('Enter "y" (overwrite) or "n" (cancel).')
    if overwrite == 'n':
        return False
    return True 


def get_data(datapath):
    print('Searching directory:',datapath)
    if not os.path.exists(datapath):
        print(datapath)
        raise Exception('Path does not exist. Aborting.')
    images = []
    for extension in SUPPORTED_EXTENSIONS:
        images.extend(glob.glob(os.path.join(datapath,extension)))
    print(f'Found {len(images)} images.')
    return images

main()
