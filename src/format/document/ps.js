import {Format} from "../../Format.js";

const _PS_MAGIC = [/^PostScript$/, /^PostScript document/];
export {_PS_MAGIC};

export class ps extends Format
{
	name         = "PostScript";
	website      = "http://fileformats.archiveteam.org/wiki/Postscript";
	ext          = [".ps"];
	mimeType     = "application/postscript";
	magic        = _PS_MAGIC;
	forbiddenExt = [".eps"];
	converters   = ["ps2pdf"];	//, "inkscape", "uniconvertor", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
