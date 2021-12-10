import {Format} from "../../Format.js";

export class rsrc extends Format
{
	name       = "MacOS Resource Fork";
	website    = "http://fileformats.archiveteam.org/wiki/Macintosh_resource_file";
	ext        = [".rsrc"];
	magic      = ["Mac OSX datafork font", "AppleDouble Resource Fork", "AppleDouble encoded Macintosh file", "Mac AppleDouble encoded"];
	converters = ["deark[opt:applesd:extractrsrc=1] -> resource_dasm", "deark"];
}
