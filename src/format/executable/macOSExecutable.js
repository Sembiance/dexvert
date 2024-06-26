import {Format} from "../../Format.js";

export class macOSExecutable extends Format
{
	name       = "MacOS Executable";
	website    = "http://fileformats.archiveteam.org/wiki/MacBinary";
	magic      = ["Macintosh Application", "Preferred Executable Format", "Format: Preferred Executable Format", /^fmt\/1070( |$)/];
	idMeta     = ({macFileType}) => ["APPL", "APPC"].includes(macFileType);
	converters = ["unar[mac][skipMacBinaryConversion]", "deark[module:macbinary][mac]"];
}
