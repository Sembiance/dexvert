import {Format} from "../../Format.js";

export class drazlace extends Format
{
	name           = "Drazlace";
	website        = "http://fileformats.archiveteam.org/wiki/Dir_Logo_Maker";
	ext            = [".drl", ".dlp"];
	forbidExtMatch = true;
	magic          = ["Drazlace bitmap"];
	converters     = ["recoil2png", "view64"];
}
