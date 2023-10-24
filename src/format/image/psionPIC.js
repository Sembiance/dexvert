import {Format} from "../../Format.js";

export class psionPIC extends Format
{
	name       = "Psion Series 3";
	website    = "http://fileformats.archiveteam.org/wiki/Psion_PIC";
	ext        = [".pic", ".icn"];
	weakExt    = [".pic", ".icn"];
	magic      = ["Psion Serie 3 bitmap"];
	converters = ["deark[module:psionpic][matchType:magic]", "recoil2png", "nconvert"];
}
