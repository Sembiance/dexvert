import {Format} from "../../Format.js";

export class ice extends Format
{
	name       = "Interlace Character Editor";
	website    = "http://fileformats.archiveteam.org/wiki/Interlace_Character_Editor_font";
	ext        = [".ice"];

	// Because it just matches a generic extension, a size check will help ensure we don't try and convert crazyiness
	// All samples are less than 2055 bytes, but we'll check anything less than 8192
	idCheck = inputFile => inputFile.size<4096;

	converters = ["recoil2png[format:ICE]"];
}
