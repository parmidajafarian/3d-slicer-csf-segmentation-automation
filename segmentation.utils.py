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