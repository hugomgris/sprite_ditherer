"""
Pack dithered finger sprites into Playdate-compatible sprite sheets
Playdate specs: any size, but commonly 16x16, 32x32, or 64x64 per frame
"""
from PIL import Image
import os
import json
import argparse

def pack_spritesheet(input_dir, output_path, sprite_width, sprite_height, columns):
	"""Pack individual sprites into a sprite sheet"""
	
	# Get all PNG files
	files = sorted([f for f in os.listdir(input_dir) if f.endswith('_dithered.png')])
	
	if not files:
		raise ValueError(f"No dithered images found in {input_dir}")
	
	# Calculate sheet dimensions
	rows = (len(files) + columns - 1) // columns
	sheet_width = sprite_width * columns
	sheet_height = sprite_height * rows
	
	# Create blank sheet
	sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
	
	# Paste sprites
	for idx, filename in enumerate(files):
		img = Image.open(os.path.join(input_dir, filename))
		
		# Resize if needed
		if img.size != (sprite_width, sprite_height):
			img = img.resize((sprite_width, sprite_height), Image.NEAREST)
		
		col = idx % columns
		row = idx // columns
		x = col * sprite_width
		y = row * sprite_height
		
		sheet.paste(img, (x, y))
	
	sheet.save(output_path)
	print(f"Packed {len(files)} sprites into {output_path}")
	print(f"Sheet size: {sheet_width}x{sheet_height} ({columns}x{rows} grid)")
	
	return {
		"sprite_count": len(files),
		"sprite_size": [sprite_width, sprite_height],
		"sheet_size": [sheet_width, sheet_height],
		"grid": [columns, rows],
		"files": files
	}

def main():
	parser = argparse.ArgumentParser(description="Pack sprites into Playdate sprite sheet")
	parser.add_argument("--input", required=True, help="Input directory with dithered sprites")
	parser.add_argument("--output", required=True, help="Output sprite sheet path")
	parser.add_argument("--width", type=int, default=64, help="Sprite width")
	parser.add_argument("--height", type=int, default=64, help="Sprite height")
	parser.add_argument("--columns", type=int, default=4, help="Columns in sheet")
	
	args = parser.parse_args()
	
	metadata = pack_spritesheet(
		args.input,
		args.output,
		args.width,
		args.height,
		args.columns
	)
	
	# Save metadata
	metadata_path = args.output.replace('.png', '_metadata.json')
	with open(metadata_path, 'w') as f:
		json.dump(metadata, f, indent=2)
	
	print(f"Metadata saved to {metadata_path}")

if __name__ == "__main__":
	main()