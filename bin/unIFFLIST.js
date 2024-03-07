import {xu} from "xu";
import {read as readIFF, write as writeIFF} from "./iffUtil.js";
import {cmdUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input> as an IFF LIST file and properly extracts each sub-file into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "IFF LIST file path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

// IFF LIST spec, kinda: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF

const iff = await readIFF(argv.inputFilePath);
if(iff.type!=="LIST")
	Deno.exit(xlog.error`Error: IFF file does not start with the expected LIST`);

for(let i=0;i<iff.iffs.length;i++)
	await writeIFF(iff.iffs[i], path.join(argv.outputDirPath, `${i.toString().padStart(iff.iffs.length.toString().length, "0")}.iff`));
