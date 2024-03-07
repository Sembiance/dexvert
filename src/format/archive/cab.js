import {Format} from "../../Format.js";

export class cab extends Format
{
	name       = "Cabinet";
	website    = "http://fileformats.archiveteam.org/wiki/Cabinet";
	ext        = [".cab"];
	magic      = [/^Microsoft Cabinet [Aa]rchive/, "CAB Archiv gefunden", /^CAB$/, /^x-fmt\/414( |$)/];
	converters = ["cabextract", "sqc", "deark[module:cab]", "izArc", "UniExtract"];
}
