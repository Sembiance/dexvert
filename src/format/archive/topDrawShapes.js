import {Format} from "../../Format.js";

export class topDrawShapes extends Format
{
	name        = "Top Draw Shapes Archive";
	website     = "http://fileformats.archiveteam.org/wiki/Top_Draw";
	ext         = [".tds", ".td"];
	magic       = ["Top Draw Shapes"];
	unsupported = true;
	notes       = "No known extractor. I could probably use the original program and figure out a way to get them out, but meh.";
}
