import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class macPaint extends Format
{
	name           = "MacPaint Image";
	website        = "http://fileformats.archiveteam.org/wiki/MacPaint";
	ext            = [".mac", ".pntg", ".pic", ".macp", ".pnt"];
	forbidExtMatch = [".pic"];
	magic          = ["MacPaint image data", "Mac MacPaint bitmap (MacBinary)", "deark: macpaint", "Apple Macintosh MacPaint :mac:", /^fmt\/(161|1429)( |$)/, /^x-fmt\/161( |$)/];
	//weakMagic      = ["deark: macpaint"];
	idMeta         = ({macFileType}) => macFileType==="PNTG";
	mimeType       = "image/x-macpaint";
	forbiddenMagic = ["Installer VISE Mac package", ...TEXT_MAGIC];
	metaProvider   = ["image"];
	converters     = [
		"deark[module:macpaint][mac][matchType:magic]", "iio2png", "wuimg[matchType:magic]", "imconv[format:mpnt][strongMatch]", "nconvert[format:mac]", `abydosconvert[format:${this.mimeType}]`, "convert",
		"keyViewPro",
		...["pv", "canvas5", "corelPhotoPaint", "tomsViewer"].map(v => `${v}[strongMatch]`)	// omit "hiJaakExpress[hasExtMatch]" as it will incorrectly handle other/venusMacro/SW.MAC
	];
	verify = ({meta}) => meta.width<8000 && meta.height<8000;
	notes  = "The MacBinary header is entirely optional, which makes this format really hard to properly detect, like those here: http://discmaster.textfiles.com/browse/8166/Educorp1Compilation.sit/educorp1/Clip%20Art_Pictures%20(4000,%207200)/4009%20Celebs%20v.2/The%20Pics!";
}
