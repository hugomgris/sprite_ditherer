"""
Finger configuration for automated pose rendering (5 fingers, basic model)
"""

FINGERS = {
	"thumb": {
		"bone_name" : "thumb_base",
		"start_angle": 0.0,
		"end_angle": -1.0,
		"rotation_axis": "x",
		"pose_count": 16
	},
	"index": {
		"bone_name": "index_base",
		"start_angle": 0.0,
		"end_angle": -1.3,
		"rotation_axis": "x",
		"pose_count": 16,
	},
	"middle": {
		"bone_name": "middle_base",
		"start_angle": 0.0,
		"end_angle": -1.3,
		"rotation_axis": "x",
		"pose_count": 16,
	},
	"ring": {
		"bone_name": "ring_base",
		"start_angle": 0.0,
		"end_angle": -1.3,
		"rotation_axis": "x",
		"pose_count": 16,
	},
	"pinky": {
		"bone_name": "pinky_base",
		"start_angle": 0.0,
		"end_angle": -1.3,
		"rotation_axis": "x",
		"pose_count": 16,
	},
}

ARMATURE_NAME = "HandRig"
CAMERA_NAME = "EXPORT_CAM"

DITHER_CONFIG = {
	"matrix": 4,
	"black_cutoff": 10,
	"white_cutoff": 170,
}