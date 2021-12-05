/*
import {Program} from "../../Program.js";

export class unlzx extends Program
{
	website = "http://xavprods.free.fr/lzx/";
	package = "app-arch/unlzx";
	flags = {"unlzxListOnly":"If set to true, only list out the the files in the archive and set meta info, don't actually extract. Default: false"};
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	moment = require("moment");

exports.meta =
{
	website       : "http://xavprods.free.fr/lzx/",
	package : "app-arch/unlzx",
	flags :
	{
		unlzxListOnly : "If set to true, only list out the the files in the archive and set meta info, don't actually extract. Default: false"
	}
};

exports.bin = () => "unlzx";
exports.args = (state, p, r, inPath=state.input.filePath) => ([r.flags.unlzxListOnly ? "-v" : "-x", inPath]);
exports.runOptions = () => ({encoding : "latin1"});

exports.post = (state, p, r, cb) =>
{
	if(!r.flags.unlzxListOnly)
		return setImmediate(cb);
	
	r.meta.fileProps = {};

	r.results.trim().split("\n").forEach(line =>
	{
		const parts = (line.match(/^\s*(?<unpackedSize>\d+)\s+(?<packedSize>\d+)\s+(?<tsTime>\S+)\s+(?<tsDate>\S+)\s+(?<attribs>\S+)\s+"(?<filename>.+)"$/) || {groups : {}}).groups;
		if(!parts.tsDate || !parts.tsTime)
			return;
		const ts = moment(`${parts.tsDate} ${parts.tsTime}`, "D-MMM-YYYY HH:mm:ss");
		r.meta.fileProps[parts.filename] = {unpackedSize : parts.unpackedSize, packedSize : parts.packedSize, ts : ts.unix(), attribs : parts.attribs};
	});

	setImmediate(cb);
};
*/
