import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class macPaint extends Format
{
	name           = "MacPaint Image";
	website        = "http://fileformats.archiveteam.org/wiki/MacPaint";
	ext            = [".mac", ".pntg", ".pic", ".macp"];
	magic          = ["MacPaint image data", "Mac MacPaint bitmap (MacBinary)", "Macintosh MacPaint", /^fmt\/(161|1429)( |$)/, /^x-fmt\/161( |$)/];
	mimeType       = "image/x-macpaint";
	forbiddenMagic = ["Installer VISE Mac package", ...TEXT_MAGIC];
	metaProvider   = ["image"];
	converters     = ["deark[mac]", `abydosconvert[format:${this.mimeType}]`, "convert", "hiJaakExpress", "pv[matchType:magic]", "corelPhotoPaint", "tomsViewer"];
	notes          = "The MacBinary header is entirely optional, which makes this format really hard to properly detect, like those here: http://discmaster.textfiles.com/browse/8166/Educorp1Compilation.sit/educorp1/Clip%20Art_Pictures%20(4000,%207200)/4009%20Celebs%20v.2/The%20Pics!";	// eslint-disable-line max-len
}
