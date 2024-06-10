import {Format} from "../../Format.js";

export class neoDrawDrawing extends Format
{
	name       = "NewDraw Drawing";
	website    = "http://fileformats.archiveteam.org/wiki/NeoDraw";
	ext        = [".teo"];
	magic      = ["NeoDraw drawing"];
	converters = ["neoDraw"];
}
