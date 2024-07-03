import {Format} from "../../Format.js";

export class riff extends Format
{
	name       = "RIFF (Generic Fallback)";
	website    = "http://fileformats.archiveteam.org/wiki/RIFF";
	magic      = ["Generic RIFF container", "RIFF Datei: unbekannter Typ", /^RIFF \((little|big)-endian\) data/, /^RIFF .*data$/, /^fmt\/1886( |$)/];
	fallback   = true;
	converters = ["deark[module:riff]"];
}
