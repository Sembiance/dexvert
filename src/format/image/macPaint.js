import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class macPaint extends Format
{
	name           = "MacPaint Image";
	website        = "http://fileformats.archiveteam.org/wiki/MacPaint";
	ext            = [".mac", ".pntg", ".pic", ".macp", ".pnt"];
	forbidExtMatch = [".pic"];
	magic          = ["MacPaint image data", "Mac MacPaint bitmap (MacBinary)", /^fmt\/(161|1429)( |$)/, /^x-fmt\/161( |$)/];
	idMeta         = ({macFileType}) => macFileType==="PNTG";
	mimeType       = "image/x-macpaint";
	forbiddenMagic = ["Installer VISE Mac package", ...TEXT_MAGIC];
	metaProvider   = ["image"];
	converters     = [
		"deark[module:macpaint][mac][matchType:magic]", "iio2png", "imconv[format:mpnt]", `abydosconvert[format:${this.mimeType}]`, "convert",
		"keyViewPro",
		...["hiJaakExpress[strongMatch][hasExtMatch]", "pv", "canvas5", "corelPhotoPaint", "tomsViewer"].map(v => `${v}[matchType:magic]`)
	];
	verify = ({meta}) => meta.width<8000 && meta.height<8000;
	notes  = "The MacBinary header is entirely optional, which makes this format really hard to properly detect, like those here: http://discmaster.textfiles.com/browse/8166/Educorp1Compilation.sit/educorp1/Clip%20Art_Pictures%20(4000,%207200)/4009%20Celebs%20v.2/The%20Pics!";
}
