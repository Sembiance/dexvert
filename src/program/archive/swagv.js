"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	moment = require("moment"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website : "http://fileformats.archiveteam.org/wiki/SWG",
	unsafe  : true
};

exports.dos = () => "SWAG/SWAGV.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath}`]);
exports.dosData = (state, p, r) => ({includeDir : true, autoExec : ["CD SWAG", `SWAGV.EXE /V ${r.args} > ..\\OUT\\DEXVERTL.TXT`]});

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
			
			fs.readFile(listFilePath, {encoding : "latin1"}, this);
		},
		function extractFiles(listContentRaw)
		{
			const pasFiles = [];
			listContentRaw.split("\n").forEach(line =>
			{
				// Num  Length   Size  %   Date    Time  CRC  Attr Subject
				//----- ------  ----- --- -------  ----- ---- ---- -----------------------------
				//(  1)  37638  10462 73% 05-28-93 13:45 7349 ---w General PASCAL FAQ
				const lineParts = (line.trim().match(/\(\s*(?<num>\d+)\)\s+(?<len>\d+)\s+(?<size>\d+)\s+(?<pct>\d+)%\s+(?<ts>\d+-\d+-\d+)\s+(?<tsTime>\d+:\d+)\s+(?<crc>\S+)\s+(?<attr>\S+)\s+(?<desc>.+)/) || {groups : null}).groups;
				if(!lineParts)
					return;
				
				pasFiles.push({num : lineParts.num, filename : `${lineParts.num.toString().padStart(4, "0")}_${lineParts.desc.replaceAll("/", "-")}.pas`, ts : moment(lineParts.ts, "MM-DD-YY")?.unix()});
			});

			r.pasFiles = pasFiles;

			fileUtil.unlink(listFilePath, this);
		},
		cb
	);
};
