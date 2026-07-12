import {Format} from "../../Format.js";

export class bitRock extends Format
{
	name           = "BitRock Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: BitRock Installer"];
	converters     = ["vibeExtract"];
}
