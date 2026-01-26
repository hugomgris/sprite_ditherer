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
	from finger_config import FINGERS, ARMATURE_NAME, CAMERA_NAME, DITHER_CONFIG
except ModuleNotFoundError:
	# Fallback: manually load and exec the config file
	print("Warning: Could not import finger_config, loading manually...")
	config_path = os.path.join(SCRIPT_DIR, "finger_config.py")
	with open(config_path, 'r') as f:
		exec(f.read(), globals())

#-----Configuration-----#
BASE_OUTPUT_DIR = "//../output"

#-----Helpers-----#
def lerp(a, b, t):
	return a + (b - a) * t

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

def get_armature():
	"""Get and validate armature object"""
	armature_obj = bpy.data.objects.get(ARMATURE_NAME)
	if armature_obj is None:
		raise RuntimeError(f"Armature '{ARMATURE_NAME}' not found")
	
	if armature_obj.type != 'ARMATURE':
		raise RuntimeError(f"'{ARMATURE_NAME}' is not an armature")
	
	return armature_obj

def render_finger(finger_name, config, scene, armature_obj):
	"""Render all poses for a single finger"""
	print(f"\n=== Rendering {finger_name.upper()} ===")
	
	# Setup output directory
	raw_output = bpy.path.abspath(os.path.join(BASE_OUTPUT_DIR, "raw", finger_name))
	os.makedirs(raw_output, exist_ok=True)
	
	# Get pose bone
	pose_bone = armature_obj.pose.bones.get(config["bone_name"])
	if pose_bone is None:
		raise RuntimeError(f"Bone '{config['bone_name']}' not found")
	
	pose_bone.rotation_mode = 'XYZ'
	
	# Store metadata
	metadata = {
		"finger": finger_name,
		"bone": config["bone_name"],
		"frames": []
	}
	
	# Render loop
	pose_count = config["pose_count"]
	for i in range(pose_count):
		t = i / (pose_count - 1)
		angle = lerp(config["start_angle"], config["end_angle"], t)
		
		# Set rotation
		axis = config["rotation_axis"]
		if axis == "x":
			pose_bone.rotation_euler.x = angle
		elif axis == "y":
			pose_bone.rotation_euler.y = angle
		elif axis == "z":
			pose_bone.rotation_euler.z = angle
		
		bpy.context.view_layer.update()
		
		# Render
		filename = f"{finger_name}_{i:02d}.png"
		scene.render.filepath = os.path.join(raw_output, filename)
		bpy.ops.render.render(write_still=True)
		
		# Store metadata
		metadata["frames"].append({
			"index": i,
			"angle": angle,
			"filename": filename
		})
		
		print(f"  Frame {i:02d}: angle = {angle:.4f}")
	
	# Reset pose
	pose_bone.rotation_euler = (0.0, 0.0, 0.0)
	bpy.context.view_layer.update()
	
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
		"--input", raw_output,
		"--output", dithered_output,
		"--matrix", str(DITHER_CONFIG["matrix"]),
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
	print(f"Available cameras: {[obj.name for obj in bpy.data.objects if obj.type == 'CAMERA']}")
	print(f"Available armatures: {[obj.name for obj in bpy.data.objects if obj.type == 'ARMATURE']}")
	
	scene = setup_scene()
	armature_obj = get_armature()

	print(f"Using armature: {armature_obj.name}")
	print(f"Available bones: {list(armature_obj.pose.bones.keys())}")
	
	bpy.context.view_layer.objects.active = armature_obj
	bpy.ops.object.mode_set(mode='POSE')
	
	results = {}
	
	# Process each finger
	for finger_name, config in FINGERS.items():
		try:
			raw_output = render_finger(finger_name, config, scene, armature_obj)
			dithered_output = run_dithering(raw_output, finger_name)
			
			results[finger_name] = {
				"raw": raw_output,
				"dithered": dithered_output,
				"status": "success"
			}
		except Exception as e:
			print(f"ERROR processing {finger_name}: {e}")
			results[finger_name] = {
				"status": "failed",
				"error": str(e)
			}
	
	# Save summary
	blend_dir = os.path.dirname(bpy.data.filepath)
	project_root = os.path.dirname(blend_dir)
	summary_path = os.path.join(project_root, "output", "export_summary.json")
	
	with open(summary_path, 'w') as f:
		json.dump(results, f, indent=2)
	
	print(f"\n=== EXPORT COMPLETE ===")
	print(f"Summary saved to {summary_path}")

main()