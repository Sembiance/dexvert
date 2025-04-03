import {Format} from "../../Format.js";

export class sng extends Format
{
	name           = "Scriptable Network Graphic";
	website        = "https://sng.sourceforge.net/";
	ext            = [".sng"];
	forbidExtMatch = true;
	magic          = ["Scriptable Network Graphics"];
	converters     = ["sng"];
}
