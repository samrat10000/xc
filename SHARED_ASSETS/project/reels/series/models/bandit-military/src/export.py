import bpy,sys,os
a=sys.argv[sys.argv.index('--')+1:]
bpy.ops.wm.open_mainfile(filepath=a[0])
bpy.ops.object.select_all(action='DESELECT')
root=bpy.data.objects['BANDIT • Armored reconnaissance buggy']; root.name='BANDIT • Military recon buggy (Night Terror)'
for o in [root]+list(root.children_recursive): o.select_set(True)
bpy.ops.export_scene.gltf(filepath=a[1], use_selection=True, export_apply=True, export_format='GLB',
    export_image_format='WEBP', export_image_quality=88, export_lights=False, export_cameras=False)
print('EXPORTED',os.path.getsize(a[1])//1024,'KB')
