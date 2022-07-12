showMessage("Select dir including all tiff image");
openDir = getDirectory("Select dir including all tiff image"); 

showMessage("Select dir including RoiSet.zip file");
 ////roiset=File.openDialog("select RoiSet.zip file");
roiset = getDirectory("Select dir including RoiSet.zip file");
roiManager("Open", roiset+"RoiSet.zip");
list = getFileList(openDir);

for (i=0; i<list.length; i++){
	open(openDir+list[i]);
	if (endsWith(list[i], ".tiff")){
		roiManager("Measure");
		close();
	}
}


saveAs("Results", roiset + "Results.csv");
