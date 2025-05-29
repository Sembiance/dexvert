import {Format} from "../../Format.js";

export class ascom extends Format
{
	name           = "ASCOM";
	website        = "http://fileformats.archiveteam.org/wiki/ASCOM";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["ASCOM", "16bit COM ASCOM text reader", "deark: ascom (ASCOM (executable text))"];
	converters     = ["deark[module:ascom][opt:text:encconv=0]"];
}
