import {Format} from "../../Format.js";
import {_EPS_MAGIC, _EPS_EXT} from "../image/eps.js";

const _PS_MAGIC = [/^PostScript$/, /^PostScript document/, /^x-fmt\/(406|408)( |$)/];
const _PS_EXT = [".ps"];
export {_PS_MAGIC, _PS_EXT};

export class ps extends Format
{
	name           = "PostScript";
	website        = "http://fileformats.archiveteam.org/wiki/Postscript";
	ext            = _PS_EXT;
	mimeType       = "application/postscript";
	magic          = _PS_MAGIC;
	forbiddenMagic = _EPS_MAGIC;
	forbiddenExt   = _EPS_EXT.subtractAll(_PS_EXT);
	converters     = ["ps2pdf"];	//, "inkscape", "uniconvertor", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
