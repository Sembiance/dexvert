import {Format} from "../../Format.js";

export class pcPaint extends Format
{
	name           = "PC Paint Image";
	website        = "http://fileformats.archiveteam.org/wiki/PCPaint_PIC";
	ext            = [".pic", ".clp"];
	forbidExtMatch = true;
	magic          = ["PC Paint/Pictor bitmap", "PC Paint Bitmap", "piped pictor sequence (pictor_pipe)", "deark: pcpaint (PCPaint", "PC Paint :pic:", /^x-fmt\/170( |$)/];
	forbiddenMagic = ["deark: bsave_cmpr"];

	// wuimg handles invisible lines like EASY1.PIC
	// deark is the only thing that appears to handle .clp files
	// nconvert sometimes fails to convert, but sometimes succeeds. same command. weird.
	converters = ["wuimg[format:pictor]", "deark[module:pcpaint]", "nconvert[format:pic]", "ffmpeg[format:pictor_pipe][outType:png]", "pv[hasExtMatch]"];
	verify     = ({meta}) => meta.height>1 && meta.width>1;
}
