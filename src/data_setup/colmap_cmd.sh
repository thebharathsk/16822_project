IMAGE_PATH=/Users/bharath/Documents/acads/fall_2023/16822_project/data/frames/drop_2
WORKSPACE_PATH=/Users/bharath/Documents/acads/fall_2023/16822_project/data/colmap/drop_2
QUALITY=high
DATA_TYPE=video
SINGLE_CAMERA=1

mkdir $WORKSPACE_PATH
colmap automatic_reconstructor --image_path $IMAGE_PATH --workspace_path $WORKSPACE_PATH --quality $QUALITY --data_type $DATA_TYPE --single_camera $SINGLE_CAMERA