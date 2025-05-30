import {Format} from "../../Format.js";

export class rpm extends Format
{
	name       = "Red Hat Package Manager Archive";
	website    = "http://fileformats.archiveteam.org/wiki/RPM";
	ext        = [".rpm"];
	magic      = [
		// generic
		"RPM Package", "RPM ", "Red Hat Package Manager Source", "Archive: RPM package", "application/x-rpm", /^RPM$/, "deark: rpm", /^fmt\/(793|794|795)( |$)/,
		
		// specific
		"Delta RPM Package"
	];
	converters = ["deark[module:rpm]", "sevenZip[renameOut]", "unar"];
}
