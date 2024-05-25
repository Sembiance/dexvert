import {Format} from "../../Format.js";

export class canvasImage extends Format
{
	name       = "Canvas Image";
	website    = "http://fileformats.archiveteam.org/wiki/Canvas";
	ext        = [".cvs", ".cv5", ".cvx", ".cvi"];
	magic      = ["Canvas Image File", "Canvas 5 document"];
	converters = ["canvas5", "canvas[matchType:magic]"];
}
