import {Format} from "../../Format.js";

export class macOSExecutable extends Format
{
	name       = "MacOS Executable";
	website    = "http://fileformats.archiveteam.org/wiki/MacBinary";
	magic      = ["Macintosh Application (MacBinary)", "Preferred Executable Format"];
	converters = ["unar[mac]", "deark"];
}
