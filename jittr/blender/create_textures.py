import bpy, bmesh, numpy, yaml


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

def xyz_to_uv(matrix, K1, K2, aspect, xyz1_array):
    xyz1_array = numpy.swapaxes(xyz1_array, 0, 1)
    uvz_array = numpy.dot(matrix, xyz1_array)
    uv_aspect_array = numpy.dot(numpy.diag([aspect, 1.0]),
                                numpy.divide(uvz_array[:2], uvz_array[2]))
    r_sqrd_array = numpy.einsum(
        'ij,ij->j', uv_aspect_array, uv_aspect_array)
    r_to4_array = numpy.einsum('i,i->i', r_sqrd_array, r_sqrd_array)
    uv_aspect_array += numpy.multiply((K1*r_sqrd_array + K2*r_to4_array),
                                      uv_aspect_array)
    uv_array = numpy.dot(numpy.diag([1/aspect, 1.0]), uv_aspect_array)
    uv_array = numpy.swapaxes(uv_array, 0, 1)
    return uv_array


def main(render, material_set):

    object = bpy.context.active_object

    # Read mtl using location specified in mtl_file in custom properties:
    materials = read_mtl(object)
    def location(object):
        mtl_file = object.data['mtl_file']
        mtl_file_name = mtl_file.split('/')[-1]
        mtl_location = mtl_file.rstrip(mtl_file_name)
        return mtl_location
    location = location(object)

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

        # Get the aspect ratio of this image.
        aspect_ratio = float(bpy.data.images[texture].size[0]) \
            / float(bpy.data.images[texture].size[1])

        # read npy file (currently unused)
        numpy_file = '%s%s.npy' % (location, material)
        def read_numpy_file(filePath):
            matrix14 = numpy.load(filePath)
            project_matrix = numpy.reshape(matrix14[:12], (3, 4))
            K1 = matrix14[12]
            K2 = matrix14[13]
            return [K1, K2, project_matrix]
        # read yaml file
        yaml_file = '%s%s.yaml' % (location, material)
        def read_yaml_file(filePath):
            doc = yaml.load(open(filePath));
            K1 = doc['K1']
            K2 = doc['K2']
            rot_matrix = numpy.array(doc['rotationMatrix'])
            translation = numpy.array(doc['translation'])
            cam_loc = numpy.dot(rot_matrix.transpose(), translation)
            project_matrix = numpy.insert(rot_matrix, 3, values=translation,
                                          axis=1)
            u0, v0 = doc['offsetU'], doc['offsetV']
            uScale, vScale = doc['scaleU'], doc['scaleV']
            calib_matrix = numpy.array([[uScale, 0.0   , u0 ],
                                        [0.0   , vScale, v0 ],
                                        [0.0   , 0.0   , 1.0]])
            project_matrix = numpy.dot(calib_matrix, project_matrix)
            return [K1, K2, project_matrix, cam_loc]  
        K1, K2, project_matrix, camera_location = read_yaml_file(yaml_file)
        #K1, K2, project_matrix = read_numpy_file(numpy_file)

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
            uv_array = xyz_to_uv(
                project_matrix, K1, K2, aspect_ratio, xyz1_array)
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

            # Bake image
            bpy.context.scene.render.bake_type = 'TEXTURE'
            bpy.ops.object.bake_image()
            bpy.data.images['bake_image'].save_render(
                filepath='%s/unwrapped/%s.png' % (location, material))

if __name__ == "__main__":
    material_set = range(0,15)
    main(True, material_set)


