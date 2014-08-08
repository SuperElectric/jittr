fix_obj.py reads files of the form: (old.mtl, old.obj), and creates files in the same directory of the form: (new.mtl, new.obj)
stitch_textures.py reads old .mtl and image textures specifed in the .mtl file, and uses imagemagick to output a new stitched texture.
Both scripts must be run in the directory of the .obj  and .mtl file. The old image textures need not be in this directory, as the mtl can specify image textures with absolute or relative paths.
It is easiest to run these by adding the following to .bashrc:
export PATH=$PATH:/full/path/to/jittr/stitch_obj_textures/
Then change directory to the folder where .obj and .mtl files are kept, and run:
fix_obj.py <arguments>
stitch_textures.py <arguments>
