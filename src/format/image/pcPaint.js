import {Format} from "../../Format.js";

export class pcPaint extends Format
{
	name           = "PC Paint Image";
	website        = "http://fileformats.archiveteam.org/wiki/PCPaint_PIC";
	ext            = [".pic", ".clp"];
	magic          = ["PC Paint/Pictor bitmap", "PC Paint Bitmap", "piped pictor sequence (pictor_pipe)", "deark: pcpaint (PCPaint", "PC Paint :pic:", /^x-fmt\/170( |$)/];
	forbiddenMagic = ["deark: bsave_cmpr"];

	// deark is the only thing that appears to handle .clp files
	// nconvert sometimes fails to convert, but sometimes succeeds. same command. weird.
	converters = ["deark[module:pcpaint]", "nconvert[format:pic][matchType:magic]", "wuimg[matchType:magic]", "ffmpeg[format:pictor_pipe][outType:png]", "pv[matchType:magic][hasExtMatch]"];
	verify     = ({meta}) => meta.height>1 && meta.width>1;
}
