import {Format} from "../../Format.js";

export class turboTXT extends Format
{
	name           = "TurboTXT";
	website        = "http://fileformats.archiveteam.org/wiki/TurboTXT";
	ext            = [".com", ".exe"];
	forbidExtMatch = true;
	magic          = ["16bit COM executable viewer TurboTXT", "deark: turbotxt"];
	converters     = ["deark[module:turbotxt][opt:text:encconv=0]"];
}
