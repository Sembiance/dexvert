import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class macPaint extends Format
{
	name           = "MacPaint Image";
	website        = "http://fileformats.archiveteam.org/wiki/MacPaint";
	ext            = [".mac", ".pntg", ".pic", ".macp", ".pnt"];
	forbidExtMatch = [".pic"];
	magic          = ["MacPaint image data", "Mac MacPaint bitmap (MacBinary)", "deark: macpaint", "Apple Macintosh MacPaint :mac:", /^fmt\/(161|1429)( |$)/, /^x-fmt\/161( |$)/];
	//weakMagic      = ["deark: macpaint", /^x-fmt\/161( |$)/];
	idMeta         = ({macFileType}) => macFileType==="PNTG";
	mimeType       = "image/x-macpaint";
	forbiddenMagic = ["Installer VISE Mac package", ...TEXT_MAGIC];
	metaProvider   = ["image"];
	converters     = [
		"deark[module:macpaint][mac][matchType:magic]", "iio2png",
		"powerpaint[format:macpaint]",	// handles 5054.pnt & 5058.pnt & 5060.pnt (only other capable converter is keyViewPro)
		"wuimg[format:mac][matchType:magic]",		// incorrectly processes non MacPaint files such as: https://discmaster.textfiles.com/view/33954/DPPCPRO0599A.ISO/May/Lotus97/LOTUS/WORDPRO/XX01252.TBL?details
		"imconv[format:mpnt][strongMatch]", "nconvert[format:mac]", `abydosconvert[format:${this.mimeType}]`, "convert",
		...["keyViewPro", "pv", "canvas5", "corelPhotoPaint", "tomsViewer"].map(v => `${v}[strongMatch]`)	// omit "hiJaakExpress[hasExtMatch]" as it will incorrectly handle other/venusMacro/SW.MAC
	];
	verify = ({meta}) => meta.width<8000 && meta.height<8000;
	notes  = "The MacBinary header is entirely optional, which makes this format really hard to properly detect, like those here: http://discmaster.textfiles.com/browse/8166/Educorp1Compilation.sit/educorp1/Clip%20Art_Pictures%20(4000,%207200)/4009%20Celebs%20v.2/The%20Pics!";
}
