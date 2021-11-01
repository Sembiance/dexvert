/*
import {Format} from "../../Format.js";

export class lottie extends Format
{
	name = "Lottie";
	website = "https://github.com/Samsung/rlottie";
	ext = [".json"];
	mimeType = "application/json";
	notes = "Will only match lottie files that include a layers property.";
	converters = ["lottie2gif"]

idCheck = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name        : "Lottie",
	website     : "https://github.com/Samsung/rlottie",
	ext         : [".json"],
	mimeType    : "application/json",
	notes       : "Will only match lottie files that include a layers property."
};

exports.idCheck = state =>
{
	try
	{
		if(JSON.parse(fs.readFileSync(state.input.absolute, XU.UTF8))?.layers)
			return true;
	}
	catch(err) {}

	return false;
};

// abydosconvert also supports this format, unfortuantely as of abydos-0.2.4 it currently doesn't animate correctly, not clearing canvas between frames
// So we just use lottie2gif instead which is included in rlottie
exports.converterPriority = ["lottie2gif"];

*/
