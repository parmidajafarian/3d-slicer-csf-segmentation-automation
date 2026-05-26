import slicer

def load_and_filter_synthseg(seg_path, keep_labels=None, output_name="SynthSeg_Segmentation"):
    """
    Load SynthSeg NIfTI, filter labels, rename segments
    """
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

# If run directly
if __name__ == "__main__":
    seg_path = "/Users/parmidajafarian/Downloads/Education/UoA/Extracurriculars/Animus/MRHead_synthseg.nii.gz"
    load_and_filter_synthseg(seg_path)