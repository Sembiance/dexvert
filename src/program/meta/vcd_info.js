/*
import {Program} from "../../Program.js";

export class vcd_info extends Program
{
	website = "https://www.gnu.org/software/vcdimager";
	gentooPackage = "media-video/vcdimager";
	gentooUseFlags = "xml";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://www.gnu.org/software/vcdimager",
	gentooPackage  : "media-video/vcdimager",
	gentooUseFlags : "xml",
	informational  : true
};

exports.bin = () => "vcd-info";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`--bin-file=${inPath}`]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	let curHeader = undefined;
	(r.results || "").trim().split("\n").filterEmpty().forEach((line, i) =>
	{
		if((/^VCD [\d.]+ detected$/).test(line.trim()))
			meta.isVCD = true;
		
		if(curHeader===null)
		{
			curHeader = line.trim();
			return;
		}

		if((/^-+$/).test(line))
		{
			if(i>0)
				curHeader = null;
			return;
		}

		const props = (line.trimEnd().match(/^\s+(?<name>[^:]+):\s+(?<val>.+)$/) || {}).groups;
		if(!curHeader || !curHeader.endsWith("primary volume descriptor") || !props)
			return;
		
		let propName = {"ID" : "id", "ISO size" : "isoSize"}[props.name] || props.name.toCamelCase().replaceAll(" ", "").trim();
		if(propName.endsWith("Id"))
			propName = `${propName.slice(0, -2)}ID`;
		meta[propName] = props.val.trimChars(["`", "'"]);
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
