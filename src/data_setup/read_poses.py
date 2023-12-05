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

def read_poses(model_path:str):
    """
    Read poses from colmap model
        model_path: path to colmap model
    """
    #time difference between frames
    t_sec = 1/190
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
    
    # #get translation vectors
    # tvecs = [pose.tvec for pose in poses.values()]
    
    #convert camera positions into a numpy array
    camera_positions = np.array(camera_positions)
    
    #get relative translation
    tvecs_rel = camera_positions[1:] - camera_positions[0]
    
    #compute magnitude of relative translations
    tvecs_rel_mag = [np.linalg.norm(tvec) for tvec in tvecs_rel]
    tvecs_rel_mag = np.array(tvecs_rel_mag)
    
    #compute velocity and acceleration
    vel = np.gradient(tvecs_rel_mag)/t_sec
    vel_ = gaussian_average(vel, 5)
    acc = np.gradient(vel)/t_sec
    acc_ = gaussian_average(acc, 5)
    jerk = np.gradient(acc)/t_sec
    jerk_ = gaussian_average(jerk, 5)
    
    #compute scale factor
    scale_factor = acc_gt/np.mean(acc)
    scale_factor_ = acc_gt/np.mean(acc_)
    
    print(f"Acceleration avg {np.mean(acc)}, Scale factor: {scale_factor}")
    print(f"Acceleration avg smooth {np.mean(acc_)}, Scale factor: {scale_factor_}")
    
    # #scale displacement, velocity, acceleration, and jerk
    tvecs_rel_mag = tvecs_rel_mag*scale_factor_
    vel = vel_*scale_factor_
    acc = acc_*scale_factor_
    
    #plot relative translation magnitudes
    plt.plot(tvecs_rel_mag)
    plt.xlabel('Frame')
    plt.ylabel('Relative translation magnitude')
    plt.savefig('cmag.png')
    plt.close()
    
    #plot velocity
    plt.plot(vel)
    plt.xlabel('Frame')
    plt.ylabel('velocity')
    plt.savefig('vel.png')
    plt.close()
    
    #plot acceleration
    plt.plot(acc)
    plt.xlabel('Frame')
    plt.ylabel('acceleration')
    plt.savefig('acc.png')
    plt.close()
    
    #plot jerk
    plt.plot(jerk)
    plt.xlabel('Frame')
    plt.ylabel('jerk')
    plt.savefig('jerk.png')
    plt.close()

    #plot all on same plot
    # plt.plot(tvecs_rel_mag, label='Relative translation magnitude')
    plt.plot(vel, label='Velocity')
    plt.plot(acc, label='Acceleration')
    plt.plot(jerk, label='Jerk')
    plt.xlabel('Frame')
    plt.legend()
    plt.savefig('all.png')
    
if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser(description='Read poses from colmap model')
    parser.add_argument('--model_path', type=str, required=True, help='path to colmap model')
    
    args = parser.parse_args()
    
    #read poses
    read_poses(args.model_path)