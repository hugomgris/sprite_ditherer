"""
Finger configuration for automated pose rendering (5 fingers + palm, split model)
"""

FINGERS = {
	"palm": {
		"collection":    "00_palm",
		"armature_name": "HandRig_palm",
		"bone_name":     "root",        # rest pose — bone is never rotated
		"start_angle":   0.0,
		"end_angle":     0.0,
		"rotation_axis": "x",
		"pose_count":    1,             # single static frame
	},
	"thumb": {
		"collection":    "01_thumb",
		"armature_name": "HandRig_thumb",
		"bone_name":     "thumb_base",
		"start_angle":   0.0,
		"end_angle":     -1.0,
		"rotation_axis": "x",
		"pose_count":    16,
	},
	"index": {
		"collection":    "02_index",
		"armature_name": "HandRig_index",
		"bone_name":     "index_base",
		"start_angle":   0.0,
		"end_angle":     -1.3,
		"rotation_axis": "x",
		"pose_count":    16,
	},
	"middle": {
		"collection":    "03_middle",
		"armature_name": "HandRig_middle",
		"bone_name":     "middle_base",
		"start_angle":   0.0,
		"end_angle":     -1.3,
		"rotation_axis": "x",
		"pose_count":    16,
	},
	"ring": {
		"collection":    "04_ring",
		"armature_name": "HandRig_ring",
		"bone_name":     "ring_base",
		"start_angle":   0.0,
		"end_angle":     -1.3,
		"rotation_axis": "x",
		"pose_count":    16,
	},
	"pinky": {
		"collection":    "05_pinky",
		"armature_name": "HandRig_pinky",
		"bone_name":     "pinky_base",
		"start_angle":   0.0,
		"end_angle":     -1.3,
		"rotation_axis": "x",
		"pose_count":    16,
	},
}

# Collections that should never be touched (camera, lights, etc.)
SHARED_COLLECTIONS = ["EXPORT_CAM", "Lights"]

CAMERA_NAME = "EXPORT_CAM"

DITHER_CONFIG = {
	"matrix":       4,
	"black_cutoff": 10,
	"white_cutoff": 170,
}