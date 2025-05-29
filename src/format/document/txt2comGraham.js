import {Format} from "../../Format.js";

export class txt2comGraham extends Format
{
	name           = "Graham's TXT2COM";
	website        = "http://fileformats.archiveteam.org/wiki/TXT2COM_(Keith_P._Graham)";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = [/Graham's TXT2COM/, "deark: txt2com (TXT2COM)"];
	converters     = ["deark[module:txt2com][opt:text:encconv=0]"];
}
