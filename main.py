import sys

project_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/3d-slicer-csf-segmentation-automation"

if project_path not in sys.path:
    sys.path.append(project_path)

from synthseg_runner import run_synthseg
from load_synthseg import load_and_filter_synthseg
from hd_bet_pipeline import run_hd_bet
from subarachnoid_segmentation import create_csf_shell
from segmentation_utils import merge_segmentations, merge_ventricles, smooth_ventricles, keep_largest_island, merge_segments_into_new, keep_only_segments


def main():
    mri_image = "MRHead"                         # Name of the MRI volume in the scene
    segmentation_name = "HD_BET_Segmentation"    # Name of your segmentation node
    segment_name = "Brain"                       # Segment to shrink      
    csf_name = "Subarachnoid Segment"            # Name of the final subarachnoid segment
    margin_mm = -3                               # Shrink amount in millimeters
    input_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/MRHead_stripped.nii.gz"
    output_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/MRHead_synthseg.nii.gz"  # Path to SynthSeg output
    synthseg_cmd = "/Applications/freesurfer/8.1.0/bin/mri_synthseg"

    print("Starting full segmentation pipeline...")

    run_synthseg(input_path, output_path, synthseg_cmd)

    # 1. Load SynthSeg
    synthseg_node = load_and_filter_synthseg(output_path)

    # 2. HD-BET (brain extraction from MRI volume in scene)
    brainSeg, brainVolume = run_hd_bet(mri_image, segmentation_name)

    # 3. CSF shell from HD-BET brain segmentation
    csf_node = create_csf_shell(segmentation_name=segmentation_name,
                     brain_segment=segment_name,
                     csf_name=csf_name,
                     margin_mm=margin_mm)
    
    print("Starting ventricle processing...")

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

    keep_largest_island("SynthSeg_Segmentation", "Left_Ventricle_Merged")
    keep_largest_island("SynthSeg_Segmentation", "Right_Ventricle_Merged")

    merge_segments_into_new(
    segmentation_name="SynthSeg_Segmentation",
    input_segments=[
        "Left_Ventricle_Merged",
        "Right_Ventricle_Merged",
        "Third_Fourth_Ventricle_Merged"
    ],
    output_name="All_Ventricles_Merged"
    )

    merge_segmentations(
    source_name="HD_BET_Segmentation",
    target_name="SynthSeg_Segmentation"
    )

    keep_only_segments(
    "SynthSeg_Segmentation",
    ["Subarachnoid Segment", "All_Ventricles_Merged"]
    )

    slicer.mrmlScene.RemoveNode(
    slicer.util.getNode("HD_BET_Brain")
    )

    print("Pipeline complete.")

if __name__ == "__main__":
    main()