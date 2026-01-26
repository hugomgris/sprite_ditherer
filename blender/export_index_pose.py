import bpy
import os
import subprocess
import sys

# -----------------------------
# Configuration
# -----------------------------
ARMATURE_OBJECT_NAME = "HandRig"
INDEX_BONE_NAME = "index_base"

POSE_COUNT = 10
START_ANGLE = 0.0
END_ANGLE = -1.3  # radians

OUTPUT_DIR = "//../output/raw/index"

CAMERA_NAME = "EXPORT_CAM"

# -----------------------------
# Helpers
# -----------------------------
def lerp(a, b, t):
	return a + (b - a) * t

# -----------------------------
# Resolve output path
# -----------------------------
output_path = bpy.path.abspath(OUTPUT_DIR)
os.makedirs(output_path, exist_ok=True)

# -----------------------------
# Validate camera
# -----------------------------
camera = bpy.data.objects.get(CAMERA_NAME)
if camera is None:
	raise RuntimeError(f"Camera '{CAMERA_NAME}' not found")

scene = bpy.context.scene
scene.camera = camera
scene.render.image_settings.file_format = 'PNG'
scene.render.use_file_extension = True

# -----------------------------
# Resolve armature object
# -----------------------------
armature_obj = bpy.data.objects.get(ARMATURE_OBJECT_NAME)
if armature_obj is None:
	raise RuntimeError(f"Object '{ARMATURE_OBJECT_NAME}' not found")

if armature_obj.type != 'ARMATURE':
	raise RuntimeError(f"Object '{ARMATURE_OBJECT_NAME}' is not an armature")

bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='POSE')

# -----------------------------
# Resolve pose bone
# -----------------------------
pose_bone = armature_obj.pose.bones.get(INDEX_BONE_NAME)
if pose_bone is None:
	raise RuntimeError(f"Pose bone '{INDEX_BONE_NAME}' not found")

pose_bone.rotation_mode = 'XYZ'

# -----------------------------
# Pose + render loop
# -----------------------------
print("Rendering index finger poses")

for i in range(POSE_COUNT):
	t = i / (POSE_COUNT - 1)
	angle = lerp(START_ANGLE, END_ANGLE, t)

	pose_bone.rotation_euler.x = angle
	bpy.context.view_layer.update()

	filename = f"index_{i:02d}.png"
	scene.render.filepath = os.path.join(output_path, filename)

	bpy.ops.render.render(write_still=True)
	print(f"Rendered pose {i}: x = {angle:.4f}")

# -----------------------------
# Reset pose
# -----------------------------
pose_bone.rotation_euler = (0.0, 0.0, 0.0)
bpy.context.view_layer.update()

print("Index finger export complete")

#-----Dithering subprocess call------#
python_exe = "python3"
blend_dir = os.path.dirname(bpy.data.filepath) # Directory containing the .blend file
project_root = os.path.dirname(blend_dir) # One level up from blender/
script = os.path.join(project_root, "processing", "dither.py")
dithered_output = os.path.join(project_root, "output", "dithered")

print(f"Calling dither script: {script}")
print(f"Input: {output_path}")
print(f"Output: {dithered_output}")


result = subprocess.run([
	python_exe, script,
	"--input",
	output_path,
	"--output",
	dithered_output,
	"--matrix",
	"2",
	"--black-cutoff",
	"10",
	"--white-cutoff",
	"170",
	], capture_output=True, text=True)
	
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

if result.returncode != 0:
	raise RuntimeError(f"Dithering failed: {result.stderr}")

print("Dithering complete")