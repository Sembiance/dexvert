"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	moment = require("moment"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website : "http://fileformats.archiveteam.org/wiki/HA"
};

exports.dos = () => "HA.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath}`]);
exports.dosData = (state, p, r) => ({autoExec : ["CD OUT", `..\\HA.EXE lf ${r.args} > DEXVERTL.TXT`, `..\\HA.EXE xy ${r.args}`]});

// HA.EXE doesn't set the date/time for each file, but it does know what they are with a list, so we manually set the date and times ourselves
exports.post = (state, p, r, cb) =>
{
	const listFilePath = path.join(state.output.absolute, "DEXVERTL.TXT");
	
	tiptoe(
		function checkExistance()
		{
			fileUtil.exists(listFilePath, this);
		},
		function loadFile(exists)
		{
			if(!exists)
				return this.finish();
			
			fs.readFile(listFilePath, {encoding : "latin1"}, this.parallel());
			fileUtil.glob(state.output.absolute, "**", {nodir : true}, this.parallel());
		},
		function setDates(listContentRaw, fileOutputPaths)
		{
			if(fileOutputPaths.length===0)
				return this.finish;
			
			if(fileOutputPaths.length===1 && fileOutputPaths.includes(listFilePath))
				return this.jump(-1);

			let seenStart = false;
			let seenEnd = false;
			let itemLineNum = null;
			let itemInfo = null;
			const itemInfos = [];
			listContentRaw.split("\n").forEach(line =>
			{
				if(seenEnd)
					return;

				if(line.startsWith("==="))
				{
					if(seenStart)
					{
						seenEnd = true;
					}
					else
					{
						itemLineNum = 0;
						itemInfo = {};
						seenStart = true;
					}

					return;
				}

				if(!seenStart)
					return;
				
				if(line.startsWith("---"))
				{
					itemInfos.push(itemInfo);
					itemLineNum = 0;
					itemInfo = {};
					return;
				}

				if(itemLineNum===null)
					return;
				
				if(itemLineNum===0)
				{
					const lineParts = line.match(/^\s*(?<filename>\S+)\s+(?<osize>\d+)\s+(?<csize>\d+)\s+(?<pct>\S+)\s%\s+(?<date>\S+)\s+(?<time>\S+)\s+.*/)?.groups;
					itemInfo.filename = lineParts.filename;
					itemInfo.ts = moment(`${lineParts.date} ${lineParts.time}`, "YYYY-MM-DD HH:mm")?.unix();
				}
				else if(itemLineNum===1)
				{
					itemInfo.dir = line.match(/^\s*(?<hash>\S+)\s+(?<dir>\S+)\s+/)?.groups?.dir?.trim();
					itemInfo.dir = (itemInfo.dir==="(none)" ? "" : itemInfo.dir.replaceAll("\\", "/"));
				}

				itemLineNum++;
			});

			itemInfos.parallelForEach((o, subcb) =>
			{
				const fileOutputPath = fileOutputPaths.find(v => path.relative(state.output.absolute, v).toLowerCase()===path.join(o.dir, o.filename));
				if(!fileOutputPath)
				{
					XU.log`Failed to find output file for HA file ${o}`;
					return setImmediate(subcb);
				}

				fs.utimes(fileOutputPath, o.ts, o.ts, subcb);
			}, this);
		},
		function cleanup()
		{
			fileUtil.unlink(listFilePath, this);
		},
		cb
	);
};
