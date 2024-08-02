import {Format} from "../../Format.js";

export class rpm extends Format
{
	name       = "Red Hat Package Manager Archive";
	website    = "http://fileformats.archiveteam.org/wiki/RPM";
	ext        = [".rpm"];
	magic      = ["RPM Package", "RPM ", "Red Hat Package Manager Source", "Archive: RPM package", /^RPM$/, /^fmt\/(794|795)( |$)/];
	converters = ["deark[module:rpm]", "sevenZip", "unar"];
}
