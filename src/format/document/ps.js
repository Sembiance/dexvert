import {Format} from "../../Format.js";

export class ps extends Format
{
	name         = "PostScript";
	website      = "http://fileformats.archiveteam.org/wiki/Postscript";
	ext          = [".ps"];
	mimeType     = "application/postscript";
	magic        = [/^PostScript$/, /^PostScript document/];
	forbiddenExt = [".eps"];
	converters   = ["ps2pdf"];	//, "inkscape", "uniconvertor", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
