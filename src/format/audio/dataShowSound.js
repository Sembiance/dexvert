import {Format} from "../../Format.js";

export class dataShowSound extends Format
{
	name           = "DataShow Sound File";
	website        = "http://www.amateur-invest.com/us_datashow.htm";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["DataShow sounds/music"];
	weakMagic      = true;
	converters     = ["vibe2wav[renameOut]"];
}
