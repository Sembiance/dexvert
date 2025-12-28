import {Format} from "../../Format.js";

export class sonyPSPTheme extends Format
{
	name           = "Sony PSP Theme";
	ext            = [".ptf"];
	forbidExtMatch = true;
	magic          = ["Sony PSP Theme file"];
	converters     = ["ptf_extract"];
}
