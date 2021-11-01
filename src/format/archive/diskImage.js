/*
import {Format} from "../../Format.js";

export class diskImage extends Format
{
	name = "Disk Image";
	website = "http://fileformats.archiveteam.org/wiki/Disk_Image_Formats";
	ext = [".img"];
	magic = ["Generic PC disk image","FAT Disk Image"];
	confidenceAdjust = undefined;
	converters = ["7z"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Disk Image",
	website : "http://fileformats.archiveteam.org/wiki/Disk_Image_Formats",
	ext     : [".img"],
	magic   : ["Generic PC disk image", "FAT Disk Image"],
	
	// 7z isn't a very reliable program with unknown data, so if we've only matched on extension, lower our confidence a lot so other format families like images have a chance
	confidenceAdjust : (state, matchType) => (matchType==="ext" ? -20 : 0)
};

exports.converterPriority = ["7z"];

*/
