"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website : "http://fileformats.archiveteam.org/wiki/SWG",
	unsafe  : true
};

exports.dos = () => "SWAG/READER.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath}`]);

exports.pre = (state, p, r, cb) =>
{
	const pasFiles = p.util.program.getRan(state, "swagv")?.pasFiles || [];

	r.dosKeys = [["Return"]];

	for(let i=0;i<pasFiles.length;i++)
	{
		r.dosKeys.push("E", `E:\\OUT\\${i}.PAS`, ["Return"]);
		if((i+1)<pasFiles.length)
			r.dosKeys.push("N");
	}

	r.dosKeys.push(["Escape"], ["Escape"]);

	setImmediate(cb);
};

// Can take some time to run, thus the 4 minute timeout
exports.dosData = (state, p, r) => ({timeout : XU.MINUTE*10, includeDir : true, autoExec : ["CD SWAG", `READER.EXE ${r.args}`], keys : r.dosKeys, keyOpts : {delay : XU.SECOND*5, interval : 100}});

exports.post = (state, p, r, cb) =>
{
	const pasFiles = p.util.program.getRan(state, "swagv")?.pasFiles || [];
	if(!pasFiles.length)
		return setImmediate(cb);

	tiptoe(
		function setDates()
		{
			pasFiles.parallelForEach((pasFile, subcb, i) =>
			{
				const pasFilePath = path.join(state.output.absolute, `${i}.PAS`);
				if(!fileUtil.existsSync(pasFilePath))
					return setImmediate(subcb);

				fs.utimes(pasFilePath, pasFile.ts, pasFile.ts, subcb);
			}, this);
		},
		function renameFiles()
		{
			pasFiles.parallelForEach((pasFile, subcb, i) =>
			{
				const pasFilePath = path.join(state.output.absolute, `${i}.PAS`);
				if(!fileUtil.existsSync(pasFilePath))
					return setImmediate(subcb);

				fs.rename(pasFilePath, path.join(state.output.absolute, pasFile.filename), subcb);
			}, this);
		},
		cb
	);
};
