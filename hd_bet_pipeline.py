import slicer
import HDBrainExtractionTool

def run_hd_bet(mri_image, segmentation_name):
    inputVolume = slicer.util.getNode(mri_image)

    logic = HDBrainExtractionTool.HDBrainExtractionToolLogic()

    brainVolume = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLScalarVolumeNode", "HD_BET_Brain"
    )

    brainSeg = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentationNode", segmentation_name
    )

    logic.setupPythonRequirements()
    logic.process(inputVolume, brainVolume, brainSeg, 0)

    # Rename segment
    segmentation = brainSeg.GetSegmentation()
    segment_id = segmentation.GetNthSegmentID(0)
    segmentation.GetSegment(segment_id).SetName("Brain")

    return brainSeg, brainVolume

if __name__ == "__main__":
    run_hd_bet("MRHead", "HD_BET_Segmentation")