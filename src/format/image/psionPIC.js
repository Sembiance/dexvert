import {Format} from "../../Format.js";

export class psionPIC extends Format
{
	name       = "Psion Series 3";
	website    = "http://fileformats.archiveteam.org/wiki/Psion_PIC";
	ext        = [".pic", ".icn"];
	weakExt    = [".pic", ".icn"];
	magic      = ["Psion Serie 3 bitmap", "deark: psionpic", "Psion Series 3 Bitmap file :psion3:", /^fmt\/1744( |$)/];
	converters = ["deark[module:psionpic][matchType:magic]", "recoil2png", "nconvert[format:psion3][matchType:magic]"];
}
