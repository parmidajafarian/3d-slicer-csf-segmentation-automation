import subprocess
import os
import sys
import slicer

def run_synthseg(input_path, output_path, synthseg_cmd):
    # -------------------------
    # Environment setup
    # -------------------------
    env = os.environ.copy()

    # FreeSurfer setup
    env["FREESURFER_HOME"] = "/Applications/freesurfer/8.1.0"
    env["PATH"] = env["FREESURFER_HOME"] + "/bin:" + env["PATH"]

    # Prevent Slicer Python contamination
    for key in [
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONEXECUTABLE",
        "PYTHONUSERBASE"
    ]:
        env.pop(key, None)

    # -------------------------
    # Checks
    # -------------------------
    if not os.path.exists(input_path):
        print(f"Input file not found:\n{input_path}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # -------------------------
    # Command
    # -------------------------
    command = [
        synthseg_cmd,
        "--i", input_path,
        "--o", output_path
    ]

    print("\nRunning SynthSeg...")
    print("Command:", " ".join(command))

    # -------------------------
    # Run (SAFE MODE)
    # -------------------------
    try:
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True,
            timeout=1800  # 30 min safety limit so it never "hangs forever"
        )

    except subprocess.TimeoutExpired:
        print("\nSynthSeg timed out (killed after 30 minutes).")
        return None

    # -------------------------
    # Output logging
    # -------------------------
    print("\n----- STDOUT -----")
    print(result.stdout)

    print("\n----- STDERR -----")
    print(result.stderr)

    print("\nExit code:", result.returncode)

    if result.returncode != 0:
        print("\nSynthSeg failed.")
        return None

    # -------------------------
    # Verify output
    # -------------------------
    if os.path.exists(output_path):
        print(f"\nDone! Output saved to:\n{output_path}")
        return output_path
    else:
        print("\nSynthSeg finished but output file not found.")
        return None


def load_and_filter_synthseg(seg_path, keep_labels=None, output_name="SynthSeg_Segmentation"):
    if keep_labels is None:
        keep_labels = {4, 5, 14, 15, 43, 44}  # Ventricle labels only
    
    # 1. Load as labelmap
    labelmap_node = slicer.util.loadLabelVolume(seg_path)
    labelmap_node.SetName("SynthSeg_Labelmap")
    
    # 2. Create segmentation node
    seg_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", output_name)
    
    # 3. Convert labelmap to segmentation
    slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(
        labelmap_node, seg_node
    )
    
    # 4. Optional 3D view
    seg_node.CreateClosedSurfaceRepresentation()
    seg_node.GetDisplayNode().SetVisibility3D(True)
    
    # 5. Clean up
    slicer.mrmlScene.RemoveNode(labelmap_node)
    
    # 6. Filter labels - keep only specified ones
    segmentation = seg_node.GetSegmentation()
    segment_ids = segmentation.GetSegmentIDs()
    
    for seg_id in segment_ids:
        segment = segmentation.GetSegment(seg_id)
        label_value = segment.GetLabelValue()
        if label_value not in keep_labels:
            segmentation.RemoveSegment(seg_id)
    
    # 7. Rename segments
    label_to_name = {
        4: "Left_Lateral_Ventricle",
        5: "Left_Inferior_Lateral_Ventricle",
        14: "Third_Ventricle",
        15: "Fourth_Ventricle",
        43: "Right_Lateral_Ventricle",
        44: "Right_Inferior_Lateral_Ventricle"
    }
    
    segmentation = seg_node.GetSegmentation()
    segment_ids = segmentation.GetSegmentIDs()
    
    for seg_id in segment_ids:
        segment = segmentation.GetSegment(seg_id)
        label_value = segment.GetLabelValue()
        if label_value in label_to_name:
            segment.SetName(label_to_name[label_value])
    
    print(f"Loaded {output_name} with {segmentation.GetNumberOfSegments()} ventricle segments")
    return seg_node