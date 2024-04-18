import {Format} from "../../Format.js";

export class inAVisionDrawing extends Format
{
	name        = "In-a-Vision Drawing";
	website     = "http://fileformats.archiveteam.org/wiki/In-A-Vision";
	ext         = [".pic"];
	magic       = ["In-a-Vision drawing", /^fmt\/1481( |$)/];
	unsupported = true;
}
