/*
import {Format} from "../../Format.js";

export class neoDeskIcon extends Format
{
	name = "NeoDesk Icon";
	website = "http://fileformats.archiveteam.org/wiki/NeoDesk_icon";
	ext = [".nic"];
	magic = ["NeoDesk icon"];
	mimeType = "image/x-neodesk-icon";
	converters = ["abydosconvert"]

idCheck = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name     : "NeoDesk Icon",
	website  : "http://fileformats.archiveteam.org/wiki/NeoDesk_icon",
	ext      : [".nic"],
	magic    : ["NeoDesk icon"],
	mimeType : "image/x-neodesk-icon"
};

exports.idCheck = (state, matches) =>
{
	// If we have a trid magic match, then we have a v3 file that starts with .NIC
	if(matches.some(match => match.magic.startsWith("NeoDesk icon") && match.from==="trid"))
		return true;

	// Otherwise we check to see if we have a v1 file that is 2088 bytes long or a v2 file which is a multiple of 244 bytes long
	const size = fs.statSync(state.input.absolute).size;
	return size===2088 || size%244===0;
};

exports.converterPriority = ["abydosconvert"];

*/
