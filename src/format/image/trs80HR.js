import {Format} from "../../Format.js";

export class trs80HR extends Format
{
	name          = "TRS-80 High-Resolution Graphic";
	website       = "http://fileformats.archiveteam.org/wiki/HR_(TRS-80)";
	ext           = [".hr"];
	magic         = ["deark: hr"];
	fileSize      = [16384, 19200, 19328, 19456];
	converters    = ["deark[module:hr]", "recoil2png", "nconvert", "tomsViewer"];
}
