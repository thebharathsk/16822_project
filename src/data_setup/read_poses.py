import os
import sys
import argparse

import numpy as np
import matplotlib.pyplot as plt

from natsort import natsorted

sys.path.append('../')
from colmap.read_write_model import read_images_binary, qvec2rotmat

def running_average(arr, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(arr, window, 'valid')

def gaussian_average(arr, window_size):
    #check that window size is odd
    if window_size % 2 == 0:
        window_size += 1
    
    #compute sigma such that the window is +/- 3 standard deviations wide
    sigma = window_size/6
    
    #position array
    pos = np.arange(-window_size//2, window_size//2+1)
    
    #compute gaussian window
    gaussian = np.exp(-(pos**2)/(2*sigma**2))
    gaussian = gaussian/np.sum(gaussian)
    
    return np.convolve(arr, gaussian, 'same')

def read_poses(model_path:str, results_path:str):
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
    t_rel = np.arange(0, len(camera_positions))*t_sec
    
    #get relative translation
    disp_rel = camera_positions - camera_positions[0]    
    disp_rel_mag = [np.linalg.norm(disp) for disp in disp_rel]
    disp_rel_mag = np.array(disp_rel_mag)
    
    #compute velocity and acceleration
    vel = np.gradient(disp_rel_mag, t_rel)
    acc = np.gradient(vel, t_rel)
    jerk = np.gradient(acc, t_rel)
    
    #smoothen measurements
    disp_rel_mag_smooth = gaussian_average(disp_rel_mag, 5)
    vel_smooth = gaussian_average(vel, 5)
    acc_smooth = gaussian_average(acc, 5)
    jerk_smooth = gaussian_average(jerk, 5)
    
    #filtered estimates
    mask = vel > 0
    vel_filtered = vel[mask]
    acc_filtered = np.gradient(vel_filtered, t_rel[mask])
    acc_filtered = acc_filtered[acc_filtered < 0]
    jerk_filtered = np.gradient(acc_filtered,)
    print(acc_filtered)
    
    #compute scale factor
    scale_factor = acc_gt/np.mean(acc)
    scale_factor_smooth = acc_gt/np.mean(acc_smooth)
    scale_factor_filtered = acc_gt/np.mean(acc_filtered)
    
    scale_factor_selected = scale_factor_smooth
     
    #scale displacement, velocity, acceleration, and jerk
    disp_rel_mag_scaled = disp_rel_mag_smooth*scale_factor_selected
    vel_scaled = vel_smooth*scale_factor_selected
    acc_scaled = acc_smooth*scale_factor_selected
    jerk_scaled = jerk_smooth*scale_factor_selected
    
    #plot relative translation magnitudes
    plt.plot(disp_rel_mag_scaled)
    plt.xlabel('Frame')
    plt.ylabel('Relative translation magnitude')
    plt.savefig(os.path.join(save_dir, 'disp.png'))
    plt.close()
    
    #plot relative translation along 3 axes
    plt.plot(disp_rel[:,0], label='x')
    plt.plot(disp_rel[:,1], label='y')
    plt.plot(disp_rel[:,2], label='z')
    plt.xlabel('Frame')
    plt.ylabel('Relative translation')
    plt.title('Relative translation along 3 axes')
    plt.legend()
    plt.savefig(os.path.join(save_dir, 'disp_xyz.png'))
    plt.close()
    
    #plot velocity
    plt.plot(vel_scaled)
    plt.xlabel('Frame')
    plt.ylabel('velocity')
    plt.savefig(os.path.join(save_dir, 'vel.png'))
    plt.close()
    
    #plot acceleration
    plt.plot(acc_scaled)
    plt.xlabel('Frame')
    plt.ylabel('acceleration')
    plt.savefig(os.path.join(save_dir, 'acc.png'))
    plt.close()
    
    #plot histogram of acceleration
    plt.hist(acc_scaled, bins=100)    
    plt.xlabel('acceleration')
    plt.ylabel('frequency')
    plt.savefig(os.path.join(save_dir, 'acc_hist.png'))
    plt.close()
    
    #plot jerk
    plt.plot(jerk_scaled)
    plt.xlabel('Frame')
    plt.ylabel('jerk')
    plt.savefig(os.path.join(save_dir, 'jerk.png'))
    plt.close()
    
    print(f"Acceleration avg before {np.mean(acc_smooth)}, after {np.mean(acc_scaled)} Scale factor: {scale_factor}")
    
if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser(description='Read poses from colmap model')
    parser.add_argument('--model_path', type=str, required=True, help='path to colmap model')
    parser.add_argument('--results_path', type=str, required=True, help='path to save results')
    
    args = parser.parse_args()
    
    #read poses
    read_poses(args.model_path, args.results_path)