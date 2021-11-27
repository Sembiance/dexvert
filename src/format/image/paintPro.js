import {Format} from "../../Format.js";

export class paintPro extends Format
{
	name          = "PaintPro";
	website       = "http://fileformats.archiveteam.org/wiki/PaintPro";
	ext           = [".pic"];
	fileSize      = 32034;
	matchFileSize = true;
	converters    = ["recoil2png"]
}
