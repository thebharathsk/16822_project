import os
import sys
import argparse

import numpy as np
import matplotlib.pyplot as plt

from natsort import natsorted

sys.path.append('../')
from colmap.read_write_model import read_images_binary, qvec2rotmat


def scale_est(model_path:str, results_path:str):
    """
    Read poses from colmap model
        model_path: path to colmap model
        results_path: path to save results
    """
    #create results directory
    save_dir  = os.path.join(results_path)
    os.makedirs(save_dir, exist_ok=True)
    
    #time difference between frames
    t_sec = 1/240
    acc_gt = 9.8
    
    #get path to binary file containing poses
    bin_path = os.path.join(model_path, 'images.bin')
    
    #read poses
    poses = read_images_binary(bin_path)
    
    #sort pose keys
    keys_sorted = natsorted(poses.keys())
    
    print(keys_sorted)
    
    #iterate through poses
    camera_positions = []
    for k in keys_sorted:
        #get qvec and tvec
        qvec = poses[k].qvec
        tvec = poses[k].tvec
        
        #get rotation matrix
        rot_mat = qvec2rotmat(qvec)
        
        #get camera position
        camera_position = -np.matmul(rot_mat.T, tvec)
        
        #store camera position
        camera_positions.append(camera_position)
        
    #convert camera positions into a numpy array
    camera_positions = np.array(camera_positions)
    
    #create time array
    t_rel = np.arange(0, len(camera_positions))* t_sec
    
    #get relative translation
    disp_rel = camera_positions - camera_positions[0]    
    disp_rel_mag = [np.linalg.norm(disp) for disp in disp_rel]
    disp_rel_mag = np.array(disp_rel_mag)
    
    #compute scale factor
    #form A matrix
    A = np.zeros((len(t_rel)-1, 2))
    A[:,0] = t_rel[1:]
    A[:,1] = -0.5*t_rel[1:]**2
    
    x = np.linalg.lstsq(A, disp_rel_mag[1:], rcond=None)[0]
    
    u = x[0]
    g_est = x[1]
    
    # g_est = np.mean((2*disp_rel_mag[1:])/(t_rel[1:]**2))
    scale_factor = acc_gt/g_est

    #scale displacement
    disp_rel_mag_scaled = disp_rel_mag*scale_factor
    disp_rel_mag_modeled = (u*t_rel - 0.5*g_est*t_rel**2)*scale_factor
    error = np.abs(disp_rel_mag_scaled - disp_rel_mag_modeled)
    mae = np.mean(error)
    rmse = np.sqrt(np.mean(error**2))
    
    #plot relative translation magnitudes
    plt.plot(t_rel, disp_rel_mag_scaled, label='estimated')
    plt.plot(t_rel, disp_rel_mag_modeled, label='model')
    plt.legend()
    plt.xlabel('Time (sec)')
    plt.ylabel('Displacement (m)')
    plt.title('Displacement obtained via COLMAP vs Kinematics model')
    plt.savefig(os.path.join(save_dir, 'disp.png'))
    plt.close()
    
    #plot relative translation along 3 axes
    plt.plot(t_rel, disp_rel[:,0], label='x')
    plt.plot(t_rel, disp_rel[:,1], label='y')
    plt.plot(t_rel, disp_rel[:,2], label='z')
    plt.xlabel('Frame')
    plt.xlabel('Time (sec)')
    plt.ylabel('Displacement (m)')
    plt.legend()
    plt.savefig(os.path.join(save_dir, 'disp_xyz.png'))
    plt.close()
    
    print('estimated u = ', u)
    print('estimated g = ', g_est)   
    print('estimated u scaled = ', u*scale_factor)
    print('estimated g scaled = ', g_est*scale_factor)
    print(f'MAD = {mae*1000} mm')
    print(f'RMSE = {rmse*1000} mm')
    
if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser(description='Read poses from colmap model')
    parser.add_argument('--model_path', type=str, required=True, help='path to colmap model')
    parser.add_argument('--results_path', type=str, required=True, help='path to save results')
    
    args = parser.parse_args()
    
    #read poses
    scale_est(args.model_path, args.results_path)