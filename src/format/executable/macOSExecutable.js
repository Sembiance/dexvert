import {Format} from "../../Format.js";

export class macOSExecutable extends Format
{
	name       = "MacOS Executable";
	website    = "http://fileformats.archiveteam.org/wiki/MacBinary";
	magic      = ["Macintosh Application (MacBinary)", "Preferred Executable Format", /^fmt\/1070( |$)/];
	converters = [
		// if it's a projector, then just extract the director files
		"director_files_extract",

		// Otherwise, try to extract the resources
		"unar[mac]",
		"deark[mac]"
	];
}
