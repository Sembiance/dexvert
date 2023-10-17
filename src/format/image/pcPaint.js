import {Format} from "../../Format.js";

export class pcPaint extends Format
{
	name    = "PC Paint Image";
	website = "http://fileformats.archiveteam.org/wiki/PCPaint_PIC";
	ext     = [".pic", ".clp"];
	magic   = ["PC Paint/Pictor bitmap", "PC Paint Bitmap", /^x-fmt\/170( |$)/];

	// deark is the only thing that appears to handle .clp files
	// nconvert sometimes fails to convert, but sometimes succeeds. same command. weird.
	converters = ["deark[module:pcpaint]", "nconvert", "pv[matchType:magic]"];
}
