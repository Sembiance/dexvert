/*
import {Program} from "../../Program.js";

export class otfinfo extends Program
{
	website = "http://www.lcdf.org/type/#typetools";
	package = "app-text/lcdf-typetools";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "http://www.lcdf.org/type/#typetools",
	package  : "app-text/lcdf-typetools",
	informational  : true
};

exports.bin = () => "otfinfo";
exports.args = (state, p, r, inPath=state.input.filePath) => (["-i", inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	(r.results || "").trim().split("\n").filterEmpty().forEach(line =>
	{
		const props = (line.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
		if(!props)
			return;

		meta[props.name.toCamelCase().replaceAll(" ", "").trim()] = props.val.trim();
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
