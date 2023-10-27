# --- In Development ---

I stoped development because I no longer wanted to use PCA in my analyses. 

Code needs review. Not thoroughly tested. 

# Easy voxelwise principal component analysis (PCA) implemented for positron emission tomography (PET) scans.

Hello and welcome to easy PCA!  
  
**Pre-reqs:** 

    1.) Register images to a template. All must be in the same space.
    2.) Normalize your data.
    3.) Images must be readable by Nibabel (nifti's are good)  
    4.) Calculate required ram utilization for the number of images you will be loading    
  
**Input:**

    1.) Path to images  Ex: /home/user/imgs or "/home/user/imgs/suvr*.nii"
    2.) Optional: A template to relice images to.
    3.) Optional: A template space volume to mask images
    4.) Optional: Specify gaussian smoothing FWHM to apply to loaded images. (Same as SPM12 smooth).

**Output:**

    1.) Top 3D principal components as compressed nifti images.  
    2.) Spreadsheets including all eigenvectors and eigenvalues.
  
Method citations: 
   http://dx.doi.org/10.1007/978-3-540-85988-8_53 
   https://doi.org/10.1212/WNL.0b013e31829e6f94    

Written by Tyler J. Ward    
 *Jagust Lab, U.C. Berkeley*
