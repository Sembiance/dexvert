import {Format} from "../../Format.js";

export class colFormatColorPalette extends Format
{
	name           = "COL Format 256 Color palette";
	ext            = [".res", ".col"];
	forbidExtMatch = true;
	magic          = ["256 Color palette", "Dark Legions Color palaette"];
	converters     = ["wuimg[format:col] -> convert[scale:1200%]"];
}
