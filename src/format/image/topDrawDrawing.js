import {Format} from "../../Format.js";

export class topDrawDrawing extends Format
{
	name        = "Top Draw Drawing";
	website     = "http://fileformats.archiveteam.org/wiki/Top_Draw";
	ext         = [".tdr", ".td"];
	magic       = ["Top Draw Drawing"];
	unsupported = true;
}
