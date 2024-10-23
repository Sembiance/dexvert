import {Format} from "../../Format.js";

export class riff extends Format
{
	name       = "RIFF (Generic Fallback)";
	website    = "http://fileformats.archiveteam.org/wiki/RIFF";
	magic      = [
		// generic
		"Generic RIFF container", "RIFF Datei: unbekannter Typ", "application/x-riff", /^RIFF \((little|big)-endian\) data/, /^RIFF .*data$/, /^fmt\/1886( |$)/,

		// specific
		"CorelSHOW Background (v5)"
	];
	fallback   = true;
	converters = ["deark[module:riff]"];
}
