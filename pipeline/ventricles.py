from segmentation_utils import (
    merge_ventricles,
    smooth_ventricles,
    keep_largest_island,
    merge_segments_into_new
)

def process_ventricles():

    # LEFT
    merge_ventricles(
        segmentation_name="SynthSeg_Segmentation",
        segment_a="Left_Lateral_Ventricle",
        segment_b="Left_Inferior_Lateral_Ventricle",
        output_name="Left_Ventricle_Merged"
    )

    smooth_ventricles(
        segmentation_name="SynthSeg_Segmentation",
        segment_name="Left_Ventricle_Merged",
        smoothing_kernel_mm=10
    )

    # RIGHT
    merge_ventricles(
        segmentation_name="SynthSeg_Segmentation",
        segment_a="Right_Lateral_Ventricle",
        segment_b="Right_Inferior_Lateral_Ventricle",
        output_name="Right_Ventricle_Merged"
    )

    smooth_ventricles(
        segmentation_name="SynthSeg_Segmentation",
        segment_name="Right_Ventricle_Merged",
        smoothing_kernel_mm=10
    )

    # MIDLINE
    merge_ventricles(
        segmentation_name="SynthSeg_Segmentation",
        segment_a="Third_Ventricle",
        segment_b="Fourth_Ventricle",
        output_name="Third_Fourth_Ventricle_Merged"
    )

    smooth_ventricles(
        segmentation_name="SynthSeg_Segmentation",
        segment_name="Third_Fourth_Ventricle_Merged",
        smoothing_kernel_mm=10
    )

    keep_largest_island(
        "SynthSeg_Segmentation",
        "Left_Ventricle_Merged"
    )

    keep_largest_island(
        "SynthSeg_Segmentation",
        "Right_Ventricle_Merged"
    )

    merge_segments_into_new(
        segmentation_name="SynthSeg_Segmentation",
        input_segments=[
            "Left_Ventricle_Merged",
            "Right_Ventricle_Merged",
            "Third_Fourth_Ventricle_Merged"
        ],
        output_name="All_Ventricles_Merged"
    )