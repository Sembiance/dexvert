import {Format} from "../../Format.js";

export class funpaint extends Format
{
	name           = "Funpaint";
	website        = "http://fileformats.archiveteam.org/wiki/Funpaint";
	ext            = [".fp2", ".fun"];
	forbidExtMatch = true;
	magic          = ["Funpaint 2 bitmap"];
	converters     = ["recoil2png", "view64"];
}
