/*
import {Program} from "../../Program.js";

export class xdftool extends Program
{
	website = "http://lallafa.de/blog/amiga-projects/amitools/";
	gentooPackage = "app-arch/amitools";
	gentooOverlay = "dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	moment = require("moment"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs");

exports.meta =
{
	website       : "http://lallafa.de/blog/amiga-projects/amitools/",
	gentooPackage : "app-arch/amitools",
	gentooOverlay : "dexvert"
};

exports.bin = () => "xdftool";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => ([inPath, "unpack", outPath]);

// The sole purpose of this function is to load the xdfmeta file and then set the appropriate timestamps on all the output files
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findMeta()
		{
			fileUtil.glob(state.output.absolute, "*.xdfmeta", this);
		},
		function readInMeta(metaFilePaths)
		{
			if(!metaFilePaths || metaFilePaths.length===0)
				return this.finish();

			fs.readFile(metaFilePaths[0], XU.UTF8, this);
		},
		function setProperDates(meta)
		{
			// Meta format: https://github.com/cnvogelg/amitools/blob/974ad59645454e2490ce155407135e1cffbe61bb/amitools/fs/MetaDB.py
			
			const lines = meta.split("\n");
			if(!lines || lines.length===0)
				return this();

			const volParts = (lines[0].match(/^(?<volName>[^:]+):(?<dosType>[^,]+),(?<ts>[^,]+),/) || {groups : {}}).groups;
			if(!volParts.volName)
				return this();

			const fallbackTS = state.input.meta.ts ? moment(state.input.meta.ts, "YYYY-MM-DD") : moment();

			let volTS = moment(volParts.ts, "DD.MM.YYYY hh:mm:ss.SS");
			if(volTS.year()>=2020)
				volTS = fallbackTS;

			fs.utimes(path.join(state.output.absolute, volParts.volName), volTS.unix(), volTS.unix(), this.parallel());
			// ROB! DENO ALERT! Need to make sure I update the DexFile.ts too!

			lines.slice(1).parallelForEach((line, subcb) =>
			{
				const parts = (line.match(/^(?<pathName>[^:]+):(?<protect>[^,]+),(?<ts>[^,]+),(?<comment>.*)$/) || {groups : {}}).groups;
				if(!parts.pathName || !parts.ts)
					return this();

				let ts = moment(parts.ts, "DD.MM.YYYY hh:mm:ss.SS");
				if(ts.year()>=2020)
					ts = fallbackTS;

				const outputFilePath = path.join(state.output.absolute, volParts.volName, parts.pathName);

				tiptoe(
					function checkExistance()
					{
						fileUtil.exists(outputFilePath, this);
					},
					function updateTimestamp(fileExists)
					{
						if(!fileExists)
							return this();

						fs.utimes(outputFilePath, ts.unix(), ts.unix(), this);
						// ROB! DENO ALERT! Need to make sure I update the DexFile.ts too!
					},
					subcb
				);
			}, this.parallel());
		},
		cb
	);
};
*/
