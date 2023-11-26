import os
import argparse

from tqdm import tqdm

def run_cmd(url:str, save_path:str):
    """Download a YouTube video from URL

    Args:
        url: url to download from
        save_path: path to save the downloaded file
    """
    cmd = f"youtube-dl -o {save_path} '{url}'"
    
    #run command and catch any errors
    try:
        os.system(cmd)
    except:
        print(f"Error downloading {url}")
        
def download_data(metadata_dir:str, save_dir:str):
    """Download the mannequin challenge dataset from the metadata file

    Args:
        metadata_dir: directory containing the metadata file
        save_dir: directory to save the downloaded videos
    """
    
    #define splits
    splits = ['train', 'validation', 'test']
    
    #iterate through splits
    for split in splits:
        if not os.path.exists(os.path.join(metadata_dir, split)):
            print(f"Metadata file for {split} split not found")
            continue
            
        print(f"Downloading {split} videos")
        
        #create save directory
        metadata_split_dir = os.path.join(metadata_dir, split)
        save_split_dir = os.path.join(save_dir, split)
        os.makedirs(save_split_dir, exist_ok=True)
        
        #list txt files
        metadata_split_files = [os.path.join(metadata_split_dir, f) for f in os.listdir(metadata_split_dir) if f.endswith('.txt')]
        
        #iterate through files
        for file_path in tqdm(metadata_split_files):
            #open file
            with open(file_path, 'r') as f:
                #read url
                url = f.readlines()[0]
                
                #save path for video
                save_path_video = os.path.join(save_split_dir, file_path.split('.')[0]+'.mp4')
                
                #download video
                run_cmd(url, save_path_video)                
    

if __name__ == "__main__":
    #parse arguments
    parser = argparse.ArgumentParser(description='Download mannequin dataset')
    parser.add_argument('--metadata_dir', type=str, default='/home/bharathsk/datasets/mannequin_challenge/metadata')
    parser.add_argument('--save_dir', type=str, default='/home/bharathsk/datasets/mannequin_challenge/videos')
    args = parser.parse_args()
    
    #download data
    download_data(args.metadata_dir, args.save_dir)