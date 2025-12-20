import slicer
import vtk
import vtkITK

segmentationName = "MRHead mask"    # Name of your segmentation node
segmentName = "Brain"               # Segment to shrink      
csfSegmentName = "CSF Segment"      # Name of the final CSF shell segment
shrunkSegmentName = "Brain Shrunk"  # Temporary shrunk segment
marginMm = -3                       # Shrink amount in millimeters

# Get Segmentation Node and Segment ID
segNode = slicer.util.getNode(segmentationName)
if not segNode:
    raise ValueError(f"Segmentation node '{segmentationName}' not found.")

segmentation = segNode.GetSegmentation()
segmentId = segmentation.GetSegmentIdBySegmentName(segmentName)
if not segmentId:
    raise ValueError(f"Segment '{segmentName}' not found.")

# Create Brain Shrunk Segment as a copy of original Brain
existingIds = set(segmentation.GetSegmentIDs())
segmentation.CopySegmentFromSegmentation(segmentation, segmentId)
newIds = set(segmentation.GetSegmentIDs())
shrunkSegmentId = list(newIds - existingIds)[0]  # The new segment ID
shrunkSegment = segmentation.GetSegment(shrunkSegmentId)
shrunkSegment.SetName(shrunkSegmentName)

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
segmentEditorNode.SetSelectedSegmentID(shrunkSegmentId)
effect.setParameter("ApplyToAllVisibleSegments", 0)
effect.setParameter("MarginSizeMm", marginMm)  # Amount to shrink
segmentEditorNode.SetOverwriteMode(segmentEditorNode.OverwriteNone)
effect.self().onApply()

# Create CSF Shell Segment as a copy of original Brain
existingIds = set(segmentation.GetSegmentIDs())
segmentation.CopySegmentFromSegmentation(segmentation, segmentId)
newIds = set(segmentation.GetSegmentIDs())
csfSegmentId = list(newIds - existingIds)[0]  # The new segment ID
csfSegment = segmentation.GetSegment(csfSegmentId)
csfSegment.SetName(csfSegmentName)

segmentation.GetSegment(csfSegmentId).SetColor(88/255, 106/255, 215/255) # Optional

# Activate Logical Operators effect
segmentEditorWidget.setActiveEffectByName("Logical operators")
effect = segmentEditorWidget.activeEffect()

# Set the destination segment in the editor node
segmentEditorNode.SetSelectedSegmentID(csfSegmentId)
effect.setParameter("ModifierSegmentID", shrunkSegmentId)
effect.setParameter("Operation", "SUBTRACT")
    
# Apply subtraction (CSF shell = original Brain - shrunk Brain)
effect.self().onApply()

# Clean up temporary nodes
segmentation.RemoveSegment(shrunkSegmentId)
slicer.mrmlScene.RemoveNode(segmentEditorNode)

print("CSF shell created successfully!")
