import {Program} from "../../Program.js";

export class svgInfo extends Program
{
	website       = "https://github.com/Sembiance/dexvert/bin/svgInfo.js";

	exec = async r =>
	{
		
	}
}


/*

#!/usr/bin/env node
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	cmdUtil = require("@sembiance/xutil").cmd,
	xmlJS = require("xml-js"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	imageUtil = require("@sembiance/xutil").image,
	fileUtil = require("@sembiance/xutil").file;

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Returns meta info about SVG at <inputFilePath>",
	opts    :
	{
		jsonOutput : {desc : "Output results as JSON instead of being human readable"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "File path to get info on", required : true}
	]});

const inputFilePath = argv.inputFilePath;
if(!fileUtil.existsSync(inputFilePath))
	return process.exit(console.error(`Input file ${inputFilePath} does not exist.`));

tiptoe(
	function convertToPNG()
	{
		this.data.pngFilePath = fileUtil.generateTempFilePath(undefined, ".png");
		runUtil.run("resvg", ["--width", "500", inputFilePath, this.data.pngFilePath], runUtil.SILENT, this);
	},
	function readAndGetInfo()
	{
		fs.readFile(argv.inputFilePath, this.parallel());
		imageUtil.getInfo(this.data.pngFilePath, {timeout : XU.SECOND*30}, this.parallel());
	},
	function getSVGInfo(fileDataRaw, pngInfo)
	{
		const svgInfo = {colorCount : pngInfo.colorCount, opaque : pngInfo.opaque};

		try
		{
			const svgData = xmlJS.xml2js(fileDataRaw, {compact : true});
			if(!svgData.svg || Object.keys(svgData.svg).filter(k => !k.startsWith("_")).length===0)
			{
				// If we have no children, doesn't matter if width/height/viewBox is set, there isn't anything to draw
				Object.assign(svgInfo, {width : 0, height : 0});
			}
			else if(svgData?.svg?._attributes?.width && svgData?.svg?._attributes?.height)
			{
				Object.assign(svgInfo, {width : +svgData.svg._attributes.width.match(/\d+/)[0], height : +svgData.svg._attributes.height.match(/\d+/)[0]});
			}
			else if(svgData?.svg?._attributes?.viewBox)
			{
				const [x, y, width, height] = svgData.svg._attributes.viewBox.split(" ").map(v => +v);
				Object.assign(svgInfo, {width : width-x, height : height-y});
			}
			else
			{
				Object.assign(svgInfo, {width : 0, height : 0});
			}

			console.log(argv.jsonOutput ? JSON.stringify(svgInfo) : svgInfo);
		}
		catch(err)
		{
			console.log(argv.jsonOutput ? JSON.stringify({err : err.toString()}) : err);
		}

		fileUtil.unlink(this.data.pngFilePath, this);
	},
	XU.FINISH
);


"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexvert/bin/svgInfo.js",
	informational : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "svgInfo.js");
exports.args = (state, p, r, inPath=state.input.filePath) => (["--jsonOutput", inPath]);
exports.post = (state, p, r, cb) =>
{
	let meta = {};
	if((r.results || "").trim().length>0)
	{
		try
		{
			const svgInfo = JSON.parse(r.results.trim());
			if(Object.keys(svgInfo.length>0))
				meta = svgInfo;
		}
		catch (err) {}
	}

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
