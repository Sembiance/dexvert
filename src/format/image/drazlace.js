import {Format} from "../../Format.js";

export class drazlace extends Format
{
	name           = "Drazlace";
	website        = "http://fileformats.archiveteam.org/wiki/Drazlace";
	ext            = [".drl", ".dlp"];
	forbidExtMatch = true;
	magic          = ["Drazlace bitmap"];
	converters     = ["recoil2png[format:DRL]", "view64"];
}
