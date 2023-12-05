import os
import sys
import argparse

import cv2 as cv2

def save_frames(video:str, output:str):
    """Convert video to frames

    Args:
        video: path to video file
        output: path to output directory
    """
    #open video
    cap = cv2.VideoCapture(video)
    
    #create output directory
    output_dir = os.path.join(output, os.path.basename(video).split(".")[0])
    os.makedirs(output_dir, exist_ok=True)
    
    #iterate through frames
    frame_num = 0
    while(cap.isOpened()):
        #read frame
        ret, frame = cap.read()
        frame_num += 1
        
        #break if no frame
        if not ret:
            break
        
        #save frame
        cv2.imwrite(os.path.join(output_dir, f"frame_{str(frame_num).zfill(3)}.jpg"), frame)

    print(f"Saved {frame_num} frames to {output_dir}")
    
if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser(description='Convert video to frames')
    parser.add_argument('--video', type=str, required=True, help='path to video file')
    parser.add_argument('--output', type=str, required=True, help='path to output directory')
    
    args = parser.parse_args()
    
    #convert video to frames
    save_frames(args.video, args.output)