"""
Full pipeline runner - can be executed from Blender or command line
"""
import subprocess
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from finger_config import FINGERS

def run_blender_export(blend_file):
	"""Run Blender export script"""
	script = os.path.join(os.path.dirname(__file__), "export_all_fingers.py")
	
	result = subprocess.run([
		"blender",
		"--background",
		blend_file,
		"--python", script
	], capture_output=True, text=True)
	
	print(result.stdout)
	if result.returncode != 0:
		print("ERROR:", result.stderr)
		return False
	return True

def pack_all_sheets(project_root):
	"""Pack sprite sheets for all fingers"""
	script = os.path.join(project_root, "processing", "pack_spritesheet.py")
	dithered_dir = os.path.join(project_root, "output", "dithered")
	sheets_dir = os.path.join(project_root, "output", "spritesheets")
	os.makedirs(sheets_dir, exist_ok=True)
	
	for finger_name in FINGERS.keys():
		input_dir = os.path.join(dithered_dir, finger_name)
		output_file = os.path.join(sheets_dir, f"{finger_name}_sheet.png")
		
		if not os.path.exists(input_dir):
			print(f"Skipping {finger_name} - no dithered images")
			continue
		
		subprocess.run([
			"python3", script,
			"--input", input_dir,
			"--output", output_file,
			"--width", "300",
			"--height", "200",
			"--columns", "4"
		], check=True)

if __name__ == "__main__":
	project_root = os.path.dirname(os.path.dirname(__file__))
	blend_file = os.path.join(project_root, "blender", "protoHand_split.blend")
	
	print("=== RUNNING FULL PIPELINE ===")
	
	# Step 1: Blender export + dithering
	if not run_blender_export(blend_file):
		sys.exit(1)
	
	# Step 2: Pack sprite sheets
	pack_all_sheets(project_root)
	
	print("\n=== PIPELINE COMPLETE ===")