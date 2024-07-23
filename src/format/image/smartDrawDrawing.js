import {Format} from "../../Format.js";

export class smartDrawDrawing extends Format
{
	name       = "SmartDraw Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/SmartDraw";
	ext        = [".sdr"];
	magic      = ["SmartDraw Drawing", "SmartDraw document", /^fmt\/623( |$)/];
	converters = ["smartDraw6"];
}
