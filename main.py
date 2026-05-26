import sys

project_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/3d-slicer-csf-segmentation-automation"

if project_path not in sys.path:
    sys.path.append(project_path)

from load_synthseg import load_and_filter_synthseg
from hd_bet_pipeline import run_hd_bet
from subarachnoid_segmentation import create_csf_shell

def main():
    mri_image = "MRHead"                         # Name of the MRI volume in the scene
    segmentation_name = "HD_BET_Segmentation"    # Name of your segmentation node
    segment_name = "Brain"                       # Segment to shrink      
    csf_name = "CSF Segment"                     # Name of the final CSF shell segment
    margin_mm = -3                               # Shrink amount in millimeters
    seg_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/MRHead_synthseg.nii.gz"  # Path to SynthSeg output

    print("Starting full segmentation pipeline...")

    # 1. Load SynthSeg
    synthseg_node = load_and_filter_synthseg(seg_path)

    # 2. HD-BET (brain extraction from MRI volume in scene)
    brainSeg, brainVolume = run_hd_bet(mri_image, segmentation_name)

    # 3. CSF shell from SynthSeg brain mask
    csf_node = create_csf_shell(segmentation_name=segmentation_name,
                     brain_segment=segment_name,
                     csf_name=csf_name,
                     margin_mm=margin_mm)
    
    print("Pipeline complete.")

if __name__ == "__main__":
    main()