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

    slicer.mrmlScene.RemoveNode(source_node)
    print(f"Deleted source segmentation: {source_name}")

    return target_node

if __name__ == "__main__":
    merge_segmentations()


def find_segment_id_by_name(segmentation, name):
    for seg_id in segmentation.GetSegmentIDs():
        if segmentation.GetSegment(seg_id).GetName() == name:
            return seg_id
    return None


def merge_ventricles(
    segmentation_name,
    segment_a,
    segment_b,
    output_name
):

    segNode = slicer.util.getNode(segmentation_name)
    segmentation = segNode.GetSegmentation()

    id_a = find_segment_id_by_name(segmentation, segment_a)
    id_b = find_segment_id_by_name(segmentation, segment_b)

    if not id_a:
        raise ValueError(f"Segment '{segment_a}' not found")
    if not id_b:
        raise ValueError(f"Segment '{segment_b}' not found")

    # Copy A as base
    existing_ids = set(segmentation.GetSegmentIDs())

    segmentation.CopySegmentFromSegmentation(segmentation, id_a)

    new_ids = set(segmentation.GetSegmentIDs())
    merged_id = list(new_ids - existing_ids)[0]

    segmentation.GetSegment(merged_id).SetName(output_name)

    # Segment Editor
    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)

    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentEditorNode"
    )

    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segNode)

    segmentEditorWidget.setActiveEffectByName("Logical operators")
    effect = segmentEditorWidget.activeEffect()

    segmentEditorNode.SetSelectedSegmentID(merged_id)

    effect.setParameter("ModifierSegmentID", id_b)
    effect.setParameter("Operation", "UNION")

    effect.self().onApply()

    slicer.mrmlScene.RemoveNode(segmentEditorNode)

    print(f"Merged {segment_a} + {segment_b} → {output_name}")

    return merged_id

if __name__ == "__main__":
    merge_ventricles()


def smooth_ventricles(
    segmentation_name,
    segment_name,
    smoothing_kernel_mm=10
):

    segNode = slicer.util.getNode(segmentation_name)
    segmentation = segNode.GetSegmentation()

    target_id = find_segment_id_by_name(segmentation, segment_name)

    if not target_id:
        raise ValueError(f"Segment '{segment_name}' not found")

    segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
    segmentEditorWidget.setMRMLScene(slicer.mrmlScene)

    segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentEditorNode"
    )

    segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
    segmentEditorWidget.setSegmentationNode(segNode)

    segmentEditorWidget.setActiveEffectByName("Smoothing")
    effect = segmentEditorWidget.activeEffect()

    segmentEditorNode.SetSelectedSegmentID(target_id)

    effect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
    effect.setParameter("KernelSizeMm", str(smoothing_kernel_mm))

    effect.self().onApply()

    slicer.mrmlScene.RemoveNode(segmentEditorNode)

    print(f"Smoothed {segment_name} ({smoothing_kernel_mm} mm)")

    return target_id

if __name__ == "__main__":
    smooth_ventricles()