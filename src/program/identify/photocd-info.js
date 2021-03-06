"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexvert",
	informational : true
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "photocd-info");
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	let meta = {};
	if((r.results || "").trim().length>0)
	{
		try
		{
			const photoCDInfo = JSON.parse(r.results.trim());
			if(Object.keys(photoCDInfo.length>0))
				meta = photoCDInfo;
		}
		catch (err) {}
	}

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
