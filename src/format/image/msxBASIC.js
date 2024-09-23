import {Format} from "../../Format.js";

export class msxBASIC extends Format
{
	name       = "MSX BASIX Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/MSX_BASIC_graphics";
	ext        = [".sc2", ".grp", ".sc3", ".sc4", ".sc5", ".ge5", ".s15", ".sc6", ".s16", ".sc7", ".ge7", ".s17", ".sc8", ".ge8", ".s18", ".sca", ".s1a", ".scc", ".srs", ".yjk", ".s1c", ".pic"];
	magic      = ["MSX BASIC Graphics bitmap", "MSX SC2/GRP", "MSX GE5/GE6", "MSX screen 7-12"];
	fileSize   = {".sc2" : [14343, 16391], ".grp" : [14343, 16391]};
	converters = ["recoil2png", "wuimg[matchType:magic]"];
}
