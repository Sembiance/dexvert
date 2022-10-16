import {Format} from "../../Format.js";
import {_OSX_DATA_FORK_FONT_MAGIC} from "../font/osXDataForkFont.js";

export class rsrc extends Format
{
	name           = "MacOS Resource Fork";
	website        = "http://fileformats.archiveteam.org/wiki/Macintosh_resource_file";
	ext            = [".rsrc", ".rs"];
	magic          = ["Mac OSX datafork font", "AppleDouble Resource Fork", "AppleDouble encoded Macintosh file", "Mac AppleDouble encoded", "Apple HFS/HFS+ resource fork", "Mac resource data", /^fmt\/(503|966)( |$)/];
	forbiddenMagic = _OSX_DATA_FORK_FONT_MAGIC;	// mis-identified as rsrc but are actually data forks
	converters     = dexState =>
	{
		const a = [];

		// If it's already an extracted resource fork, skip striaght to resource_dasm
		if(dexState.ids.some(id => id.magic==="Apple HFS/HFS+ resource fork") || dexState.original.input.ext.toLowerCase()===".rs")
			a.push("resource_dasm");

		return [...a, "deark[opt:applesd:extractrsrc=1] -> resource_dasm", "deark"];	// , "unar"
	};
}
