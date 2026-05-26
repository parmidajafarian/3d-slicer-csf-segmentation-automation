import slicer
import vtk
import vtkITK

def create_csf_shell(segmentation_name="HD_BET_Segmentation", 
                     brain_segment="Brain",
                     csf_name="CSF Segment",
                     margin_mm=-3):

    # Get segmentation node
    segNode = slicer.util.getNode(segmentation_name)
    segmentation = segNode.GetSegmentation()
    
    # Get Segmentation Node and Segment ID
    if not segNode:
        raise ValueError(f"Segmentation node '{segmentation_name}' not found.")

    # Check if Brain segment exists (if not, need to create it from ventricles)
    segmentId = segmentation.GetSegmentIdBySegmentName(brain_segment)
    if not segmentId:
        raise ValueError(f"Segment '{brain_segment}' not found.")
    
    # Create Brain Shrunk Segment as a copy of original Brain
    existingIds = set(segmentation.GetSegmentIDs())
    segmentation.CopySegmentFromSegmentation(segmentation, segmentId)
    newIds = set(segmentation.GetSegmentIDs())
    shrunkId = list(newIds - existingIds)[0]
    segmentation.GetSegment(shrunkId).SetName("Brain Shrunk")
    
    # Set up Segment Editor to subtract shrunk Brain from CSF shell
    slicer.app.processEvents()
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segNode)
    
    # Shrink Brain Segment
    segmentEditorWidget.setActiveEffectByName("Margin")
    effect = segmentEditorWidget.activeEffect()
    segmentEditorNode.SetSelectedSegmentID(shrunkId)
    effect.setParameter("ApplyToAllVisibleSegments", 0)
    effect.setParameter("MarginSizeMm", margin_mm)  # Amount to shrink
    segmentEditorNode.SetOverwriteMode(segmentEditorNode.OverwriteNone)
    effect.self().onApply()
    
    # Create CSF Shell Segment as a copy of original Brain
    existingIds = set(segmentation.GetSegmentIDs())
    segmentation.CopySegmentFromSegmentation(segmentation, segmentId)
    newIds = set(segmentation.GetSegmentIDs())
    csfSegmentId = list(newIds - existingIds)[0]  # The new segment ID
    csfSegment = segmentation.GetSegment(csfSegmentId)
    csfSegment.SetName(csf_name)
    segmentation.GetSegment(csfSegmentId).SetColor(88/255, 106/255, 215/255) # Optional

    # Activate Logical Operators effect
    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()

    # Set the destination segment in the editor node
    segmentEditorNode.SetSelectedSegmentID(csfSegmentId)
    effect.setParameter("ModifierSegmentID", shrunkId)
    effect.setParameter("Operation", "SUBTRACT")
        
    # Apply subtraction (CSF shell = original Brain - shrunk Brain)
    effect.self().onApply()
    
    # Clean up: remove shrunk segment and segment editor node
    slicer.mrmlScene.RemoveNode(segmentEditorNode)
    segmentation.RemoveSegment(shrunkId)
    
    print("CSF shell created successfully!")
    return csfSegmentId

if __name__ == "__main__":
    create_csf_shell()

import slicer

def merge_segmentations(
    source_name="HD_BET_Segmentation",
    target_name="SynthSeg_Segmentation"
):
    source_node = slicer.util.getNode(source_name)
    target_node = slicer.util.getNode(target_name)

    source_seg = source_node.GetSegmentation()
    target_seg = target_node.GetSegmentation()

    # copy every segment from source -> target
    segment_ids = source_seg.GetSegmentIDs()

    for seg_id in segment_ids:
        target_seg.CopySegmentFromSegmentation(
            source_seg,
            seg_id
        )

    print(f"Merged {len(segment_ids)} segments into {target_name}")
    return target_node

if __name__ == "__main__":
    merge_segmentations()