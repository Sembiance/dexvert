import {Format} from "../../Format.js";

export class inAVisionDrawing extends Format
{
	name        = "In-a-Vision Drawing";
	website     = "http://fileformats.archiveteam.org/wiki/In-A-Vision";
	ext         = [".pic"];
	magic       = ["In-a-Vision drawing", /^fmt\/1481( |$)/];
	notes       = "In-a-Vision and the Micrografx Windows Convet program (both on winworld) are both Windows 1.x/2.x programs that don't work in Win2k. Not aware of anything else that can convert these, as Micrografx Designer 4 does not.";
	unsupported = true;
}
