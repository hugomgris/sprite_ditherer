from PIL import Image
import numpy as np
import os
import argparse

#-----Bayer Matrices-----#
BAYER_2x2 = np.array([
	[0, 2],
	[3, 1]
])

BAYER_4x4 = np.array([
	[ 0,  8,  2, 10],
	[12,  4, 14,  6],
	[ 3, 11,  1,  9],
	[15,  7, 13,  5]
])

#-----Dithering-----#
def ordered_dither(
	image: Image.Image,
	bayer: np.ndarray,
	black_cutoff: int,
	white_cutoff: int
) -> Image.Image:

	image = image.convert("RGBA")
	r, g, b, a = image.split()

	gray = Image.merge("RGB", (r, g, b)).convert("L")
	pixels = np.array(gray, dtype=np.float32)
	alpha = np.array(a, dtype=np.uint8)

	h, w = pixels.shape
	t_h, t_w = bayer.shape
	matrix_size = t_h * t_w

	output = np.zeros((h, w), dtype=np.uint8)

	for y in range(h):
		for x in range(w):
			if alpha[y, x] < 5:
				continue

			pixel = pixels[y, x]

			if pixel <= black_cutoff:
				continue

			if pixel >= white_cutoff:
				output[y, x] = 255
				continue

			threshold = bayer[y % t_h, x % t_w]
			threshold_value = (threshold + 0.5) / matrix_size * 255

			output[y, x] = 255 if pixel > threshold_value else 0

	result = Image.fromarray(output, mode="L")
	result = Image.merge(
		"RGBA",
		(result, result, result, Image.fromarray(alpha))
	)

	return result

#-----CLI-----#
def main():
	parser = argparse.ArgumentParser(description="Ordered dithering for RGBA images")
	parser.add_argument("--input", required=True, help="Input directory")
	parser.add_argument("--output", required=True, help="Output directory")
	parser.add_argument("--matrix", type=int, choices=[2, 4], default=4)
	parser.add_argument("--black-cutoff", type=int, default=10)
	parser.add_argument("--white-cutoff", type=int, default=170)

	args = parser.parse_args()

	bayer = BAYER_2x2 if args.matrix == 2 else BAYER_4x4

	os.makedirs(args.output, exist_ok=True)

	for filename in sorted(os.listdir(args.input)):
		if not filename.lower().endswith(".png"):
			continue

		input_path = os.path.join(args.input, filename)
		output_name = filename.replace(".png", "_dithered.png")
		output_path = os.path.join(args.output, output_name)

		print(f"Dithering {filename}")

		image = Image.open(input_path)
		dithered = ordered_dither(
			image,
			bayer,
			args.black_cutoff,
			args.white_cutoff
		)
		dithered.save(output_path)

	print("Dithering complete")

if __name__ == "__main__":
	main()
