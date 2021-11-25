/*
import {Format} from "../../Format.js";

export class vidcom64 extends Format
{
	name = "Vidcom 64";
	website = "http://fileformats.archiveteam.org/wiki/Vidcom_64";
	ext = [".vid"];
	mimeType = "image/x-vidcom-64";
	magic = ["Drazpaint (C64) bitmap"];
	weakMagic = true;
	fileSize = 10050;

	converters = ["nconvert","recoil2png",`abydosconvert[format:${this.mimeType}]`,"view64"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "Vidcom 64",
	website             : "http://fileformats.archiveteam.org/wiki/Vidcom_64",
	ext                 : [".vid"],
	mimeType            : "image/x-vidcom-64",
	magic               : ["Drazpaint (C64) bitmap"], // Shares same magic identifier as Drazpaint
	weakMagic           : true,
	fileSize            : 10050,

};

// nconvert produces clearer output compared to recoil2png
exports.converterPriority = ["nconvert", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "view64"];

*/
