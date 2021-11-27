import {Format} from "../../Format.js";

export class funnyPaint extends Format
{
	name           = "Funny Paint";
	website        = "http://fileformats.archiveteam.org/wiki/Funny_Paint";
	ext            = [".fun"];
	forbidExtMatch = true;
	magic          = ["Funny Paint"];
	converters     = ["recoil2png"]
}
