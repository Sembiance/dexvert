import {Format} from "../../Format.js";
import {_OSX_DATA_FORK_FONT_MAGIC} from "../font/osXDataForkFont.js";

const APPLE_DOUBLE_MAGIC = ["AppleDouble Resource Fork", "AppleDouble encoded Macintosh file", "Mac AppleDouble encoded"];

export class rsrc extends Format
{
	name           = "MacOS Resource Fork";
	website        = "http://fileformats.archiveteam.org/wiki/Macintosh_resource_file";
	ext            = [".rsrc", ".rs"];
	magic          = ["Mac OSX datafork font", ...APPLE_DOUBLE_MAGIC, "Apple HFS/HFS+ resource fork", "Mac resource data", "Mac AIFF audio", /^fmt\/(503|966)( |$)/];
	forbiddenMagic = _OSX_DATA_FORK_FONT_MAGIC;	// mis-identified as rsrc but are actually data forks
	converters     = dexState =>
	{
		const a = [];

		if(dexState.hasMagics(APPLE_DOUBLE_MAGIC))
			a.push("deark[module:applesd][opt:applesd:extractrsrc=1]");

		return [...a, "resource_dasm", "deark[module:macrsrc]"];	// , "unar"
	};
}
