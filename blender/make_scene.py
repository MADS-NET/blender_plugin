# Builds block_6dof.blend: a solid block driven in 6-DoF by the MADS blender
# sink plugin through NodeOSC.
#
#   blender --background --factory-startup --python blender/make_scene.py
#
# Expected MADS frames (keypaths become OSC addresses):
#   {"position": [x, y, z], "rotation": [rx, ry, rz]}
#   -> /position x y z   (metres)
#   -> /rotation rx ry rz (radians, XYZ Euler)
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(HERE, "block_6dof.blend")

# Load NodeOSC from the project root so its scene properties exist, without
# touching the user's add-on preferences.
sys.path.insert(0, ROOT)
import NodeOSC  # noqa: E402

NodeOSC.register()

scene = bpy.context.scene
for obj in [o for o in scene.objects if o.name == "Cube"]:
    bpy.data.objects.remove(obj)

bpy.ops.mesh.primitive_cube_add(size=1)
block = bpy.context.active_object
block.name = "Block"
block.scale = (1.0, 0.6, 0.3)  # asymmetric, so orientation is readable
bpy.ops.object.transform_apply(scale=True)  # keep scale out of the pose
block.rotation_mode = "XYZ"
mat = bpy.data.materials.new("BlockMaterial")
mat.diffuse_color = (0.8, 0.35, 0.1, 1.0)
block.data.materials.append(mat)

envars = scene.nodeosc_envars
envars.udp_in = "0.0.0.0"  # accept the plugin from any host
envars.port_in = 9001  # plugin default
envars.autorun = True  # start listening when the file is opened

for address, prop in (("/position", "location"),
                      ("/rotation", "rotation_euler")):
    key = scene.NodeOSC_keys.add()
    key.osc_address = address
    key.osc_direction = "INPUT"
    key.data_path = f"bpy.data.objects['Block'].{prop}"
    key.osc_index = "()"  # all args, in order; NodeOSC's default "())" is invalid

bpy.ops.wm.save_as_mainfile(filepath=OUT)
print(f"saved {OUT}")
