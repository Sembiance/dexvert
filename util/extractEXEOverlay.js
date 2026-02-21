import {xu} from "xu";
import {extractEXEOverlay} from "../src/exeOverlayUtil.js";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Extracts the overlay portion of an exe",
	args :
	[
		{argid : "inputFilePath", desc : "Input file to extract", required : true},
		{argid : "outputFilePath", desc : "Location to save overlay data", required : true}
	]});

await extractEXEOverlay(argv.inputFilePath, argv.outputFilePath);
