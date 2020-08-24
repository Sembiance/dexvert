"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://www.lcdf.org/type/#typetools",
	gentooPackage  : "app-text/lcdf-typetools",
	gentooUseFlags : "kpathsea",
	informational  : true
};

exports.bin = () => "otfinfo";
exports.args = (state, p, inPath=state.input.filePath) => (["-i", inPath]);
exports.post = (state, p, cb) =>
{
	const meta = {};
	((state.run.otfinfo || [])[0] || "").trim().split("\n").filterEmpty().forEach(line =>
	{
		const props = (line.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
		if(!props)
			return;

		meta[props.name.toCamelCase().replaceAll(" ", "").trim()] = props.val.trim();
	});

	if(Object.keys(meta).length>0)
		state.run.meta.otfinfo = meta;

	setImmediate(cb);
};
