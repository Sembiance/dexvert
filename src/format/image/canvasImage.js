import {Format} from "../../Format.js";

export class canvasImage extends Format
{
	name       = "Canvas Image";
	website    = "http://fileformats.archiveteam.org/wiki/Canvas";
	ext        = [".cvi"];
	magic      = ["Canvas Image File"];
	converters = ["canvas"];
}
