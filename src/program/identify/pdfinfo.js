/*
import {Program} from "../../Program.js";

export class pdfinfo extends Program
{
	website = "https://poppler.freedesktop.org/";
	gentooPackage = "app-text/poppler";
	gentooUseFlags = "cairo curl cxx introspection jpeg jpeg2k lcms png qt5 tiff utils";
	informational = true;
}
*/

/*
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
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	
	const NUMS = ["pages", "pagerot"];
	const BOOLS = ["tagged", "userproperties", "suspects", "javascript", "encrypted", "optimized"];
	(r.results || "").trim().split("\n").filterEmpty().forEach(infoLine =>
	{
		const infoProps = (infoLine.trim().match(/^(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
		if(!infoProps)
			return;

		const propKey = infoProps.name.toLowerCase().replaceAll(" ", "");
		if(propKey==="filesize")
			return;

		meta[propKey] = NUMS.includes(propKey) ? +infoProps.val : (BOOLS.includes(propKey) ? infoProps.val==="yes" : infoProps.val);
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
