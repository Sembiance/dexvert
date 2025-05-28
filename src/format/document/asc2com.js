import {Format} from "../../Format.js";

export class asc2com extends Format
{
	name           = "Asc2Com (MorganSoft)";
	website        = "http://fileformats.archiveteam.org/wiki/Asc2Com";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["16bit COM executable Asc2Com", "Asc2Com (MorganSoft)"];
	converters     = ["deark[module:asc2com][opt:text:encconv=0]"];
}
