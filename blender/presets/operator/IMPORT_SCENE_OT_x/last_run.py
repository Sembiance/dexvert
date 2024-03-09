import bpy
op = bpy.context.active_operator

op.show_tree = False
op.show_templates = False
op.show_geninfo = False
op.do_not_add_unused_material = False
op.quickmode = False
op.parented = True
op.bone_maxlength = 1.0
op.chunksize = '2048'
op.naming_method = '0'
op.use_ngons = True
op.use_edges = True
op.use_smooth_groups = True
op.use_split_objects = True
op.use_split_groups = True
op.use_groups_as_vgroups = False
op.use_image_search = True
op.split_mode = 'ON'
op.global_clamp_size = 0.0
op.axis_forward = '-Z'
op.axis_up = 'Y'
