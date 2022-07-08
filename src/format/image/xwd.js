import {Format} from "../../Format.js";

export class xwd extends Format
{
	name         = "X Window Dump";
	website      = "http://fileformats.archiveteam.org/wiki/XWD";
	ext          = [".xwd", ".dmp", ".xdm"];
	safeExt      = ".xwd";
	mimeType     = "image/x-xwindowdump";
	magic        = ["X-Windows Screen Dump", "X-Window screen dump image data", "XWD X Windows Dump image data", /^fmt\/401( |$)/];
	weakMagic    = ["X-Windows Screen Dump"];
	metaProvider = ["image"];

	// GIMP does the best for most input files. It doesn't get the colors right on MARBLE.XPM, but it does well with bettyboop
	// nconvert handles the color of MARBLE.XPM well but messes up bettyboop and woman-with-ban.
	// All the other converters do less well
	converters = ["gimp", "nconvert", `abydosconvert[format:${this.mimeType}]`, "convert", "hiJaakExpress"];

	// Some files are confused for XWD files and produce just a black image
	verify = ({meta}) => meta.colorCount>1;
}
