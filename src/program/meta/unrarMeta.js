/*
import {Program} from "../../Program.js";

export class unrarMeta extends Program
{
	website = "https://www.rarlab.com/rar_add.htm";
	package = "app-arch/unrar";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://www.rarlab.com/rar_add.htm",
	package : "app-arch/unrar",
	informational : true
};

exports.bin = () => "unrar";
exports.args = (state, p, r, inPath=state.input.filePath) => (["lt", inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
exports.post = (state, p, r, cb) =>
{
	const meta = {files : {}};
	let fileName = null;
	const NUMBER_FIELDS = ["size", "packedSize"];
	(r.results || "").trim().split("\n").forEach(line =>
	{
		const {k, v} = (line.trim().match(/^\s*(?<k>[^:]+):\s*(?<v>.+)$/) || {groups : {}}).groups;
		if(!k || !v)
			return;

		const key = k.trim().toCamelCase();
		const val = NUMBER_FIELDS.includes(key) ? +v.trim() : v.trim();

		if(key==="name")
		{
			fileName = val;
			meta.files[fileName] = {};
		}
		else if(fileName)
		{
			meta.files[fileName][key] = val;
		}
		else
		{
			meta[key] = val;
		}
	});

	if(Object.values(meta.files).some(file => (file.flags || "").toLowerCase().includes("encrypted")))
		meta.passwordProtected = true;

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
