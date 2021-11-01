/*
import {Format} from "../../Format.js";

export class corelThumbnails extends Format
{
	name = "Corel Thumbnails Archive";
	website = "http://fileformats.archiveteam.org/wiki/CorelDRAW";
	filename = ["_thumbnail_"];
	unsupported = true;
	notes = "\nContains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them.\nEven went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed.\nSent an email to the libcdr creators, to see if they know of any info on the format, but never heard back.";
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name        : "Corel Thumbnails Archive",
	website     : "http://fileformats.archiveteam.org/wiki/CorelDRAW",
	filename    : ["_thumbnail_"],
	unsupported : true,
	notes       : XU.trim`
		Contains a bunch of 'CDX' files that each start with CDRCOMP1. Wasn't able to locate anything on the internet that can process or open them.
		Even went so far as to install Corel ArtShow and tried to reverse engineer the DLL it uses (CDRFLT40.DLL) but failed.
		Sent an email to the libcdr creators, to see if they know of any info on the format, but never heard back.`
};

*/
