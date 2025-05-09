import {Format} from "../../Format.js";

export class fontMania extends Format
{
	name           = "Font Mania Font";
	website        = "http://fileformats.archiveteam.org/wiki/Font_Mania_(REXXCOM)";
	ext            = [".com"];
	forbidExtMatch = true;
	magic          = ["Font Mania Font", "16bit DOS Font Mania font loader Command"];
	converters     = ["deark[module:fontmania]"];
}
