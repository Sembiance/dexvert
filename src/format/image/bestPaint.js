import {Format} from "../../Format.js";

export class bestPaint extends Format
{
	name          = "Best Paint";
	ext           = [".bp"];
	fileSize      = [4083];
	matchFileSize = true;
	converters    = ["recoil2png[format:BP]"];
}
