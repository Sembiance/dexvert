import {Format} from "../../Format.js";

export class drawIt extends Format
{
	name          = "DrawIt";
	ext           = [".dit"];
	fileSize      = 3845;
	matchFileSize = true;
	converters    = ["recoil2png"]
}
