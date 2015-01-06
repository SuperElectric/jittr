import bpy, bmesh, numpy, yaml
import matplotlib.image as mpimg

# set JITTR_DIR
JITTR_DIR = "/home/daniel/urop/jittr"

def read_mtl(object):
    # returns list of (material, image) pairs
    mtl_file = object.data['mtl_file']
    file = open(mtl_file)
    lines = file.readlines()
    current_material = ''
    current_texture = ''
    materials = []
    textures = []
    for line in lines:
        words = line.rstrip().split()
        if words[0] == 'newmtl':
            current_material = words[1]
        elif words[0] == 'map_Kd':
            current_texture = words[1]
            if current_material not in materials:
                materials.append(current_material)
                textures.append(current_texture)
    return list(zip(materials, textures))

def xyz_to_uv(xyz1_array, RT_matrix, calib_matrix, K1, K2):
    xyz1_array = numpy.swapaxes(xyz1_array, 0, 1)
    uvz_array = numpy.dot(RT_matrix, xyz1_array)
    uv_array = numpy.array([numpy.divide(uvz_array[0], uvz_array[2]),
                            numpy.divide(uvz_array[1], uvz_array[2])])
    r_sqrd_array = numpy.einsum(
        'ij,ij->j', uv_array, uv_array)
    r_to4_array = numpy.einsum('i,i->i', r_sqrd_array, r_sqrd_array)
    uv_array += numpy.multiply((K1*r_sqrd_array + K2*r_to4_array),
                                      uv_array)
    u_scale, v_scale, u0, v0  = [calib_matrix[0][0], calib_matrix[1][1],
                                 calib_matrix[0][2], calib_matrix[1][2]]
    uv_array = numpy.array([u0 + u_scale*uv_array[0], v0 + v_scale*uv_array[1]])
    uv_array = numpy.swapaxes(uv_array, 0, 1)
    return uv_array

def open_as_arrays(colour_texture_list, weight_texture_list):
    colour_array = numpy.array([], dtype='float32')
    weight_array = numpy.array([], dtype='float32')
    for colour_texture in colour_texture_list:
        colour_array = numpy.append(colour_array, mpimg.imread(colour_texture))
    for weight_texture in weight_texture_list:
        weight_texture_array = mpimg.imread(weight_texture).swapaxes(0,2).swapaxes(1,2)[0]
        weight_array = numpy.append(weight_array, weight_texture_array)
    single_texture_array = mpimg.imread(colour_texture_list[0])
    height = numpy.shape(single_texture_array)[0]
    width = numpy.shape(single_texture_array)[1]
    new_colour_shape = [len(colour_texture_list), height, width, 4]
    colour_array = colour_array.reshape(new_colour_shape)
    new_weight_shape = [len(colour_texture_list), height, width]
    weight_array = weight_array.reshape(new_weight_shape)
    return [colour_array, weight_array]
        

def blend_soft_max(colour_array, weight_array, K):
    weight_array = numpy.exp(K*weight_array)
    weight_array = numpy.divide(weight_array, numpy.sum(weight_array,axis=0))
    colour_array = numpy.einsum('ijkl,ijk->jkl', colour_array, weight_array)
    #colour_array = numpy.sum(colour_array,axis=0)
    return colour_array


def main(object, render=True, blend_textures=True, material_set=[]):
    # Make sure required material, texture, bake image, and locationLamp all exist
    # and are set up correctly
    
    # Set renderer to Blender internal
    if bpy.context.mode == 'EDIT_MESH':
        bpy.ops.object.editmode_toggle()
    bpy.context.scene.render.engine = 'BLENDER_RENDER'
    # Check mtl custom property exists, and if not, use default name
    if 'mtl_file' not in object.data:
        object.data['mtl_file'] = '%s/modelfiles/%s/%s_raw.mtl' % (JITTR_DIR ,object.name, object.name)
    # remove all object material slots (not completely necessary, so might change)
    for material_slot in object.material_slots:
        bpy.ops.object.material_slot_remove()
    # Create texture, materials and UVmaps, and smartuvproject UVnew
    if 'temp_material' not in bpy.data.materials:
        bpy.data.materials.new('temp_material')
        bpy.data.materials['temp_material'].diffuse_intensity = 1.0
        bpy.data.materials['temp_material'].specular_intensity = 0.0
        bpy.data.materials['temp_material'].diffuse_color = (1,1,1)
    if 'temp_texture' not in bpy.data.textures:
        bpy.data.textures.new('temp_texture', 'IMAGE')
    if 'UVold' not in object.data.uv_textures:
        if len(object.data.uv_textures) == 8:
            for tex in object.data.uv_textures:
                object.data.uv_textures.remove(tex)
        object.data.uv_textures.new('UVold')
    if 'UVnew' not in object.data.uv_textures:
        if len(object.data.uv_textures) == 8:
            for tex in object.data.uv_textures:
                object.data.uv_textures.remove(tex)
            object.data.uv_textures.new(name='UVold')
        object.data.uv_textures.new(name='UVnew')
        # Now set active UV to UVnew, enter edit mode, uv unwrap, then exit edit mode
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        object.data.uv_textures['UVnew'].active = True
        bpy.ops.uv.smart_project()
        bpy.ops.object.editmode_toggle()
    # create bake image
    if 'bake_image' not in bpy.data.images:
        bpy.data.images.new('bake_image', 1024, 1024)
    # create locationLamp (the reconstructed camera location)
    if 'locationLamp' not in bpy.data.objects:
        bpy.ops.object.lamp_add(type='POINT')
        bpy.context.active_object.name = 'locationLamp'
        bpy.data.objects['locationLamp'].parent = object
        bpy.data.objects['locationLamp'].data.falloff_type = 'CONSTANT'
        bpy.data.objects['locationLamp'].data.shadow_method = 'RAY_SHADOW'
        bpy.data.objects['locationLamp'].data.shadow_ray_samples = 4
        bpy.data.objects['locationLamp'].data.shadow_soft_size = 0
        bpy.data.objects['locationLamp'].data.shadow_ray_sample_method = 'CONSTANT_QMC'
        # bpy.data.objects['locationLamp'].scale = [10,10,10]
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = object
        object.select = True
    # Make sure that the relevant UVmaps, textures, materials etc are selected/active
    # where necessary
    bpy.data.textures['temp_texture'].type  = 'IMAGE'
    bpy.ops.object.material_slot_add()
    object.material_slots[0].material = bpy.data.materials['temp_material']
    bpy.context.object.active_material = bpy.data.materials['temp_material']
    try:
        bpy.data.materials['temp_material'].texture_slots[0].texture = bpy.data.textures['temp_texture']
    except AttributeError:
        bpy.data.materials['temp_material'].texture_slots.add()
        bpy.data.materials['temp_material'].texture_slots[0].texture = bpy.data.textures['temp_texture']
    bpy.data.materials['temp_material'].texture_slots[0].texture_coords = 'UV'
    bpy.data.materials['temp_material'].texture_slots[0].uv_layer = 'UVold'
    bpy.data.materials['temp_material'].active_texture_index = 0
    for i in range (len(bpy.data.materials['temp_material'].texture_slots)):
        if i == 0:
            bpy.context.object.active_material.use_textures[i] = True
        else:
            bpy.context.object.active_material.use_textures[i] = False
    for uv_face in object.data.uv_textures.active.data:
        uv_face.image = bpy.data.images['bake_image']

    # Read mtl using location specified in mtl_file in custom properties:
    materials = read_mtl(object)
    def location(object):
        mtl_file = object.data['mtl_file']
        mtl_file_name = mtl_file.split('/')[-1]
        mtl_location = mtl_file.rstrip(mtl_file_name)
        return mtl_location
    location = location(object)
    colour_texture_list = []
    weight_texture_list = []
    
    if material_set == []:
        material_set = range(len(materials))
    else:
        material_set = [m for m in material_set if m in range(len(materials))]
    for materialID in material_set:
        material, texture = materials[materialID]
        colour_texture_list.append('%sunwrapped/%s.png' % (location, material))
        weight_texture_list.append('%sunwrapped/%s_w.png' % (location, material))

    # Enter edit mode:
    if bpy.context.mode != 'EDIT_MESH':
        bpy.ops.object.editmode_toggle()

    # For each material in turn, project UVs and bake to new image.
    for materialID in material_set:
        material, texture = materials[materialID]

        # Set texture source to correct image
        # Set active UV to UVold
        def filepath(file, location):
            if file[0] == '/': return file
            else: return '%s%s' % (location, file)
        def directory(file, location):
            if file[0] == '/':
                file_name = file.split('/')[-1]
                return file.rstrip(file_name)
            else: return location
        if texture in bpy.data.images:
            bpy.data.images[texture].filepath = filepath(texture, location)
        else:
            bpy.ops.image.open(filepath=filepath(texture, location),
                               directory=directory(texture, location),
                               files=[{'name':texture}],
                               relative_path=True)
        bpy.data.textures['temp_texture'].image = bpy.data.images[texture]
        object.data.uv_textures['UVold'].active = True

        # read yaml file
        yaml_file = '%s%s_raw.obj.yaml' % (location, object.name)
        def read_from_yaml_file(filePath, materialName):
            doc = yaml.load(open(filePath));
            doc = doc[materialName]
            K1 = doc['K1']
            K2 = doc['K2']
            rot_matrix = numpy.array(doc['rotationMatrix'])
            translation = numpy.array(doc['translation'])
            cam_loc = -numpy.dot(rot_matrix.transpose(), translation)
            RT_matrix = numpy.insert(rot_matrix, 3, values=translation,
                                          axis=1)
            u0, v0 = doc['offsetU'], doc['offsetV']
            uScale, vScale = doc['scaleU'], doc['scaleV']
            calib_matrix = numpy.array([[uScale, 0.0   , u0 ],
                                        [0.0   , vScale, v0 ],
                                        [0.0   , 0.0   , 1.0]])
            return [RT_matrix, calib_matrix, K1, K2, cam_loc] 
        RT_matrix, calib_matrix, K1, K2, camera_location = read_from_yaml_file(yaml_file, material)
        
        # Move lamp called 'locationLamp' to the correct position
        bpy.context.scene.frame_current = materialID
        bpy.data.objects['locationLamp'].location = camera_location
        bpy.data.objects['locationLamp'].keyframe_insert(data_path='location',
            frame=materialID)
            

        # Calculate UVs
        def set_uvs():
            me = object.data
            bm = bmesh.from_edit_mesh(me)
            uv_layer = bm.loops.layers.uv.verify()
            bm.faces.layers.tex.verify()
            xyz1_list = []
            for f in bm.faces:
                for l in f.loops:
                    xyz = list(l.vert.co.xyz)
                    xyz.append(1.0)
                    xyz1_list.append(xyz)
            xyz1_array = numpy.array(xyz1_list)
            uv_array = xyz_to_uv(xyz1_array, RT_matrix, calib_matrix, K1, K2)
            index = 0
            for f in bm.faces:
                for l in f.loops:
                    l[uv_layer].uv = uv_array[index]
                    index += 1
            bmesh.update_edit_mesh(me)
        set_uvs()

        if render:

            # Set active texture to UVnew
            object.data.uv_textures['UVnew'].active = True

            # Bake images:
            # First surface colour texture
            bpy.data.materials['temp_material'].use_textures[0] = True
            bpy.context.scene.render.bake_type = 'TEXTURE'
            bpy.context.scene.display_settings.display_device = 'sRGB'
            bpy.ops.object.bake_image()
            bpy.data.images['bake_image'].save_render(
                filepath='%sunwrapped/%s.png' % (location, material))
            # Then greyscale weight texture
            bpy.data.materials['temp_material'].use_textures[0] = False
            bpy.context.scene.render.bake_type = 'FULL'
            bpy.context.scene.display_settings.display_device = 'None'
            bpy.ops.object.bake_image()
            bpy.context.scene.display_settings.display_device = 'sRGB'
            bpy.data.images['bake_image'].save_render(
            filepath='%sunwrapped/%s_w.png' % (location, material))
    
    if blend_textures:
        colour_array, weight_array = open_as_arrays(colour_texture_list, weight_texture_list)
        blended_image = blend_soft_max(colour_array, weight_array, 10.0)
        mpimg.imsave('%sunwrapped/merged.png' % location, blended_image)
        


if __name__ == "__main__":
    object = bpy.context.active_object
    main(object, render=True, blend_textures=True)



