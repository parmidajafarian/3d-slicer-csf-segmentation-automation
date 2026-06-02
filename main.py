from pathlib import Path
import sys

project_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/3d-slicer-csf-segmentation-automation"

if project_path not in sys.path:
    sys.path.append(project_path)

import slicer
from pipeline.synthseg import run_synthseg, load_and_filter_synthseg
from pipeline.hd_bet import run_hd_bet
from pipeline.subarachnoid import create_subarachnoid_shell
from pipeline.ventricles import process_ventricles
from segmentation_utils import merge_segmentations, keep_only_segments

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
    
    # 1. Run SynthSeg (if needed)
    if not Path(input_path).exists():
        run_synthseg(input_path, output_path, synthseg_cmd)

    # 1. # 2. Load and filter SynthSeg segmentation
    synthseg_node = load_and_filter_synthseg(output_path)

    # 3. Run HD-BET brain extraction
    brainSeg, brainVolume = run_hd_bet(mri_image, segmentation_name)

    # 4. Create subarachnoid CSF shell from HD-BET brain segmentation
    csf_node = create_subarachnoid_shell(segmentation_name=segmentation_name,
                     brain_segment=segment_name,
                     csf_name=csf_name,
                     margin_mm=margin_mm)
    
    # 5. Process ventricles from SynthSeg
    print("Starting ventricle processing...")
    process_ventricles()

    # 6. Merge HD-BET and SynthSeg segmentations
    print("\nMerging segmentations...")
    merge_segmentations(
    source_name="HD_BET_Segmentation",
    target_name="SynthSeg_Segmentation"
    )

    # 7. Keep only required segments (subarachnoid and ventricles)
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