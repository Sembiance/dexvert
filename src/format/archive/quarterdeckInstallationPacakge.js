import {Format} from "../../Format.js";

export class quarterdeckInstallationPacakge extends Format
{
	name       = "Quarterdeck Installation Package";
	website    = "http://fileformats.archiveteam.org/wiki/QIP_(Quarterdeck)";
	ext        = [".qip"];
	magic      = ["Quarterdeck Installation Package", "deark: qip"];
	converters = ["deark[module:qip]"];
}
