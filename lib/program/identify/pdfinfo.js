"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://poppler.freedesktop.org/",
	gentooPackage  : "app-text/poppler",
	gentooUseFlags : "cairo curl cxx introspection jpeg jpeg2k lcms png qt5 tiff utils",
	informational  : true
};

exports.bin = () => "pdfinfo";
exports.args = (state, p, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};
	
	const NUMS = ["pages", "pagerot"];
	const BOOLS = ["tagged", "userproperties", "suspects", "javascript", "encrypted", "optimized"];
	((state.run.pdfinfo || [])[0] || "").trim().split("\n").filterEmpty().forEach(infoLine =>
	{
		const infoProps = (infoLine.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
		if(!infoProps)
			return;

		const propKey = infoProps.name.toLowerCase().replaceAll(" ", "");
		if(propKey==="filesize")
			return;

		meta[propKey] = NUMS.includes(propKey) ? +infoProps.val : (BOOLS.includes(propKey) ? infoProps.val==="yes" : infoProps.val);
	});

	if(Object.keys(meta).length>0)
		state.run.meta.pdfinfo = meta;

	setImmediate(cb);
};
