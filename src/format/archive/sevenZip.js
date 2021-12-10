import {Format} from "../../Format.js";

export class sevenZip extends Format
{
	name       = "7-Zip Archive";
	website    = "http://fileformats.archiveteam.org/wiki/7z";
	ext        = [".7z"];
	mimeType   = "application/x-7z-compressed";
	magic      = ["7Zip format", "7-zip archive data", "7-Zip compressed archive"];
	converters = ["sevenZip"];
}
