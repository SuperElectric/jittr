Instructions:
 Set environment variable "JITTR_DIR" to this directory
 To run Panda3d version:
  - run "make_dataset.py" outside of Blender
  - or run "make_dataset.py --models truck shuttle mouse horse" for all 4 models
 To run Blender version:
  - Open "make_dataset.blend" and click "run"
  - Click in 3d viewport and use arrow keys or press Alt+a to see camera positions change
  - Press Numpad 0 to switch to camera view
  - Press Shift+z to see rendered view 



Jittr - Just In Time Training Renderer
(Feel free to rename :) )

The goal of this tool is to generate training imagery for training neural networks for object detection.

The initial milestone will be to make an offline tool that takes a number of 3D models, and generates something like the small NORB dataset:
http://www.cs.nyu.edu/~ylclab/data/norb-v1.0-small/

This tool will render each object from a number of viewpoints and lighting conditions. The viewpoints are constrained to a hemisphere of fixed radius.

The second milestone will be to include variations in camera distance, object position, and background imagery, like the big NORB dataset:
http://www.cs.nyu.edu/~ylclab/data/norb-v1.0/index.html

Ultimately, we would like to have the renderer be fast enough to operate in "real-time", i.e. produce training imagery as fast as the neural network can process it. This distinguishes it from most renderers which put an emphasis on costly sophistications such as multi-path reflection and surface BRDF simulation. Such a renderer would put the dataset "in the loop" of training, as the neural network could then deliberately request training imagery it is having difficulty with, in order to overcome those difficulties. I believe this would be a novel and promising avenue of machine learning research.
