import bpy
import os
import json
import subprocess
import sys

# Handle both file execution and text editor execution
try:
	SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
	# When run from Blender's text editor or console, __file__ doesn't exist
	SCRIPT_DIR = os.path.dirname(os.path.abspath(bpy.data.filepath))

# Ensure the script directory is in Python path
if SCRIPT_DIR not in sys.path:
	sys.path.insert(0, SCRIPT_DIR)

# Try to import, if it fails, load manually
try:
	from finger_config import FINGERS, SHARED_COLLECTIONS, CAMERA_NAME, DITHER_CONFIG
except ModuleNotFoundError:
	print("Warning: Could not import finger_config, loading manually...")
	config_path = os.path.join(SCRIPT_DIR, "finger_config.py")
	with open(config_path, 'r') as f:
		exec(f.read(), globals())

#-----Configuration-----#
BASE_OUTPUT_DIR = "//../output"

# All top-level finger collection names, derived from config
FINGER_COLLECTIONS = [cfg["collection"] for cfg in FINGERS.values()]

#-----Helpers-----#
def lerp(a, b, t):
	return a + (b - a) * t

def set_active_collection(target_collection_name):
	"""
	Disable every finger collection, then enable only the target one.
	Collections listed in SHARED_COLLECTIONS are never touched.
	Works on top-level scene collections.
	"""
	scene = bpy.context.scene

	for layer_collection in scene.view_layers[0].layer_collection.children:
		name = layer_collection.name

		# Never hide shared collections (camera, lights, etc.)
		if name in SHARED_COLLECTIONS:
			continue

		# Hide all finger collections except the active one
		if name in FINGER_COLLECTIONS:
			layer_collection.exclude = (name != target_collection_name)

	print(f"  Active collection: {target_collection_name}")

def setup_scene():
	"""Configure render settings"""
	camera = bpy.data.objects.get(CAMERA_NAME)
	if camera is None:
		raise RuntimeError(f"Camera '{CAMERA_NAME}' not found")

	scene = bpy.context.scene
	scene.camera = camera
	scene.render.image_settings.file_format = 'PNG'
	scene.render.use_file_extension = True

	return scene

def get_armature(armature_name):
	"""Get and validate a named armature object"""
	armature_obj = bpy.data.objects.get(armature_name)
	if armature_obj is None:
		raise RuntimeError(
			f"Armature '{armature_name}' not found. "
			f"Available armatures: {[o.name for o in bpy.data.objects if o.type == 'ARMATURE']}"
		)
	if armature_obj.type != 'ARMATURE':
		raise RuntimeError(f"'{armature_name}' is not an armature")
	return armature_obj

def render_finger(finger_name, config, scene):
	"""Activate the finger's collection, grab its armature, render all poses."""
	print(f"\n=== Rendering {finger_name.upper()} ===")

	# --- Collection switch ---
	set_active_collection(config["collection"])

	# --- Armature ---
	armature_obj = get_armature(config["armature_name"])
	bpy.context.view_layer.objects.active = armature_obj
	bpy.ops.object.mode_set(mode='POSE')

	# Setup output directory
	raw_output = bpy.path.abspath(os.path.join(BASE_OUTPUT_DIR, "raw", finger_name))
	os.makedirs(raw_output, exist_ok=True)

	# Get pose bone
	pose_bone = armature_obj.pose.bones.get(config["bone_name"])
	if pose_bone is None:
		raise RuntimeError(
			f"Bone '{config['bone_name']}' not found in '{config['armature_name']}'. "
			f"Available bones: {list(armature_obj.pose.bones.keys())}"
		)

	pose_bone.rotation_mode = 'XYZ'

	# Store metadata
	metadata = {
		"finger":    finger_name,
		"armature":  config["armature_name"],
		"collection": config["collection"],
		"bone":      config["bone_name"],
		"frames":    []
	}

	# Render loop
	pose_count = config["pose_count"]
	for i in range(pose_count):
		t = i / (pose_count - 1) if pose_count > 1 else 0.0
		angle = lerp(config["start_angle"], config["end_angle"], t)

		axis = config["rotation_axis"]
		if axis == "x":
			pose_bone.rotation_euler.x = angle
		elif axis == "y":
			pose_bone.rotation_euler.y = angle
		elif axis == "z":
			pose_bone.rotation_euler.z = angle

		bpy.context.view_layer.update()

		filename = f"{finger_name}_{i:02d}.png"
		scene.render.filepath = os.path.join(raw_output, filename)
		bpy.ops.render.render(write_still=True)

		metadata["frames"].append({
			"index":    i,
			"angle":    angle,
			"filename": filename
		})

		print(f"  Frame {i:02d}: angle = {angle:.4f}")

	# Reset pose
	pose_bone.rotation_euler = (0.0, 0.0, 0.0)
	bpy.context.view_layer.update()

	# Back to object mode before switching collections
	bpy.ops.object.mode_set(mode='OBJECT')

	# Save metadata
	metadata_path = os.path.join(raw_output, f"{finger_name}_metadata.json")
	with open(metadata_path, 'w') as f:
		json.dump(metadata, f, indent=2)

	print(f"  Metadata saved to {metadata_path}")
	return raw_output

def run_dithering(raw_output, finger_name):
	"""Run dithering subprocess for a finger"""
	print(f"\n=== Dithering {finger_name.upper()} ===")

	blend_dir = os.path.dirname(bpy.data.filepath)
	project_root = os.path.dirname(blend_dir)
	script = os.path.join(project_root, "processing", "dither.py")
	dithered_output = os.path.join(project_root, "output", "dithered", finger_name)

	result = subprocess.run([
		"python3", script,
		"--input",        raw_output,
		"--output",       dithered_output,
		"--matrix",       str(DITHER_CONFIG["matrix"]),
		"--black-cutoff", str(DITHER_CONFIG["black_cutoff"]),
		"--white-cutoff", str(DITHER_CONFIG["white_cutoff"]),
	], capture_output=True, text=True)

	if result.returncode != 0:
		print("STDERR:", result.stderr)
		raise RuntimeError(f"Dithering failed for {finger_name}")

	print(f"  Dithered images saved to {dithered_output}")
	return dithered_output

#-----Main-----#
def main():
	print(f"Available cameras:   {[o.name for o in bpy.data.objects if o.type == 'CAMERA']}")
	print(f"Available armatures: {[o.name for o in bpy.data.objects if o.type == 'ARMATURE']}")
	print(f"Top-level collections: {[c.name for c in bpy.context.scene.view_layers[0].layer_collection.children]}")

	scene = setup_scene()
	results = {}

	for finger_name, config in FINGERS.items():
		try:
			raw_output      = render_finger(finger_name, config, scene)
			dithered_output = run_dithering(raw_output, finger_name)

			results[finger_name] = {
				"raw":      raw_output,
				"dithered": dithered_output,
				"status":   "success"
			}
		except Exception as e:
			print(f"ERROR processing {finger_name}: {e}")
			results[finger_name] = {
				"status": "failed",
				"error":  str(e)
			}

	# Save summary
	blend_dir    = os.path.dirname(bpy.data.filepath)
	project_root = os.path.dirname(blend_dir)
	summary_path = os.path.join(project_root, "output", "export_summary.json")

	with open(summary_path, 'w') as f:
		json.dump(results, f, indent=2)

	print(f"\n=== EXPORT COMPLETE ===")
	print(f"Summary saved to {summary_path}")

main()