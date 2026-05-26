import slicer
import HDBrainExtractionTool

def main():
    inputVolume = slicer.util.getNode("MRBrainTumor1")

    logic = HDBrainExtractionTool.HDBrainExtractionToolLogic()

    brainVolume = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLScalarVolumeNode", "HD_BET_Brain"
    )

    brainSeg = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLSegmentationNode", "HD_BET_Segmentation"
    )

    logic.setupPythonRequirements()
    logic.process(inputVolume, brainVolume, brainSeg, 0)

if __name__ == "__main__":
    main()