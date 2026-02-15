import {Format} from "../../Format.js";

export class rleTRE extends Format
{
	name           = "Run Length Encoded True Colour Picture";
	website        = "http://fileformats.archiveteam.org/wiki/Spooky_Sprites";
	ext            = [".tre"];
	forbidExtMatch = true;
	magic          = ["Run length encoded True Colour Picture bitmap"];
	converters     = ["wuimg[format:tre]", "recoil2png[format:tre]"];
}
