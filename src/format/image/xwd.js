import {Format} from "../../Format.js";

export class xwd extends Format
{
	name         = "X Window Dump";
	website      = "http://fileformats.archiveteam.org/wiki/XWD";
	ext          = [".xwd", ".dmp", ".xdm"];
	safeExt      = ".xwd";
	mimeType     = "image/x-xwindowdump";
	magic        = ["X-Windows screen dump", "X-Window screen dump image data", "XWD X Windows Dump image data", "piped xwd sequence (xwd_pipe)", "deark: xwd", /^X Window Dump \((Direct|Pseudo|True) Color\) :xwd:$/, "X Window Dump (Static Grey) :xwd:",
		/^fmt\/401( |$)/
	];
	metaProvider = ["image"];

	// GIMP does the best for most input files
	// iio2png also does great
	// nconvert handles the color of MARBLE.XPM well but messes up bettyboop and woman-with-ban.
	// All the other converters do less well
	converters = [
		"gimp", "iio2png", "deark[module:xwd]", "wuimg[format:xwd]", "imconv[format:xwd][matchType:magic]", "nconvert[format:xwd]", "ffmpeg[format:xwd_pipe][outType:png]", `abydosconvert[format:${this.mimeType}]`, "convert",
		"hiJaakExpress[matchType:magic][hasExtMatch]"
	];

	// Some files are confused for XWD files and produce just a black image
	verify = ({meta}) => meta.colorCount>1;
}
