### 29 November

1. Solutions
    1. Frames -> COLMAP -> compute scale factor using kinematics model
    2. Frames -> COLMAP -> filter outlier accelerations -> compute scale factor using kinematics model
    3. Frames -> COLMAP -> apply kinematics correction -> filter outlier accelerations -> compute scale factor using kinematics model
    4. Frames -> COLMAP -> apply kinematics correction -> filter outlier accelerations  -> compute scale factor using kinematics model

2. Bundle adjustment constraint
    1. typical_objective = ||x_reproj - x_gt||^2 + ||y_reproj - y_gt||^2
    2. our_objective = typical_objective + kinematics
    3. kinematics = ||derivative(derivative(derivative(camera_position)))-0||^2 = ||derivative(derivative(derivative(c)))-0||^2
    4. c = -R.T*t

3. Papers
    1. https://www.sciencedirect.com/science/article/pii/S003039921830224X