import {xu} from "xu";
import {XLog} from "xlog";
import {cmdUtil} from "xutil";
import {getEXEOverlayOffset} from "../src/dexUtil.js";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Print out the byte offset where the EXE overlay starts",
	args :
	[
		{argid : "inputFilePath", desc : "EXE to process", required : true}
	]
});

const overlayStartOffset = await getEXEOverlayOffset(argv.inputFilePath);
if(overlayStartOffset)
{
	xlog.info`Overlay offset: ${overlayStartOffset}`;
	xlog.info`hexyl -s ${overlayStartOffset} -n 128 "${argv.inputFilePath}"`;
}
