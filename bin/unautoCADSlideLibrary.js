import {xu} from "xu";
import {cmdUtil, runUtil} from "xutil";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input.slb> as an AutoCAD Slide Library and extracts it into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "SLB file path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});


const {stderr} = await runUtil.run("sldtoppm", ["-dir", argv.inputFilePath]);
let seenHeader=false;
const filenames = new Set();
for(const line of stderr.split("\n"))
{
	if(line==="sldtoppm: Slides in library:")
	{
		seenHeader = true;
		continue;
	}

	if(!seenHeader)
		continue;
	
	const {filename} = line.match(/sldtoppm: {3}(?<filename>.+)/)?.groups || {};
	if(!filename)
		continue;

	filenames.add(filename);
}

await Array.from(filenames).parallelMap(async filename => await runUtil.run("sldtoppm", ["-Lib", filename, argv.inputFilePath], {stdoutEncoding : "binary", stdoutFilePath : path.join(argv.outputDirPath, `${filename}.ppm`)}));
