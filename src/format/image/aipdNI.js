import {Format} from "../../Format.js";

export class aipdNI extends Format
{
	name           = "AIPD National Instruments Image";
	website        = "http://fileformats.archiveteam.org/wiki/AIPD";
	ext            = [".apd", ".aipd"];
	forbidExtMatch = true;
	magic          = ["AIPD bitmap"];
	converters     = ["wuimg"];
}
