import {Format} from "../../Format.js";

export class nokiaGroupGraphics extends Format
{
	name       = "Nokia Group Graphics Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Nokia_Group_Graphic";
	ext        = [".ngg"];
	magic      = ["Nokia Group Graphics bitmap", "deark: ngg", "Nokia Group Graphics :ngg:"];
	converters = ["deark[module:ngg]", "nconvert[format:ngg]"];
}
