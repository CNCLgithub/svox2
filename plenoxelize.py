import numpy as np
import trimesh

mesh_path = '/gpfs/milgram/scratch60/yildirim/ajr226/svox2_singularity/SMPL_meshes/S6_WalkDog.60457274_000531.obj'
mesh = trimesh.load(mesh_path)

# .0035 because it will get all dimensions <=512. 
# This should be generalized at some point to just scale based on mesh dimensions
#but assuming all SMPL meshes are the same size it will be fine for a while
voxel_data = mesh.voxelized(0.0035)
voxel_data.fill() # make solid. Plenoxels likes solid 

#making plenoxels representation from scratch
numCells = voxel_data.sparse_indices.shape[0]
densities = np.ndarray((numCells, 1), np.float32)
density_value = 100.0 #semi-arbitrary density to initialize all voxels to
# 100.0 makes it so all parts of the body are visible, and the areas with
#fewer voxels are actually somewhat transparent, which is nice because it 
#helps see details which would be invisible in a straight silhouette
# probably changing to 200.0 would make it more silhouette-like
densities.fill(density_value)

sh_num = 9 #how many sh coefficients. Default 9, haven't tried other values
sh_coeffs = np.ndarray((numCells, sh_num * 3), np.float16)
sh_coeffs.fill(0.0) #0.0 is grey. Works decently well w. white background

#unsure if this is an SMPL thing or a trimesh thing but the y and z are swapped

# to center
x_offset = int((512 - voxel_data.shape[0])/2)
y_offset = int((512 - voxel_data.shape[2])/2)
z_offset = int((512 - voxel_data.shape[1])/2)

# constructing 2 things here: a 512 x 512 x 512 array of 'links', in which each item is either -2 ('no voxel here')
#or a positive number, in which case the density of that voxel is in that index of density_data
#so if you're looking at the voxel at 200, 200, 200, you look in links[200][200][200] and see 11546, 
#and your density is in density_data[11546]. So too with sh_data for SH coefficients.
# so each time we find an occupied voxel, counter increments by 1 to keep track of which index to store 
#densities and sh coefficients in.
counter = 0
# art for artificial, so as to avoid saying 'links = links' when saving
art_links = np.ndarray((512, 512, 512), np.int32)
art_links.fill(-2) #arbitrary negative number. As far as i can tell no difference b/t -2 and any other neg number
for index in voxel_data.sparse_indices: #only the occupied voxels (faster than iterating over the whole 512^3 voxel grid)
    art_links[index[0] + x_offset, index[2] + y_offset, index[1] + z_offset] = counter
    counter += 1

# Unsure what makes radius tick exactly, but this worked for the SMPL mesh I tested. Smaller values zoom out, bigger zoom in.
# Putting in non-identical values warps rendered images.
art_radius = np.array([0.2, 0.2, 0.2], np.float32)

art_center = np.array([0.0, 0.0, 0.0], np.float32)
art_basis = np.array(1)
# can also get components of the checkpoint from a previous version
# prev_data = np.load('ckpt/ckpt.npz')
# art_basis = prev_data['basis_type']

# you may need to create the directory and empty ckpt.npz file to save to before running this 
np.savez('ckpt/artificial/ckpt.npz', radius=art_radius, center=art_center, links=art_links, density_data=densities, sh_data=sh_coeffs, basis_type=art_basis)