import {Format} from "../../Format.js";

export class cyberPaintSeq extends Format
{
	name       = "Cyber Paint Sequence";
	website    = "http://fileformats.archiveteam.org/wiki/Cyber_Paint_Sequence";
	ext        = [".seq"];
	magic      = ["Cyber Paint Sequence", /^fmt\/1557( |$)/];
	converters = ["seq2mp4"];
}
