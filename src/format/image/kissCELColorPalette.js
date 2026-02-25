import {Format} from "../../Format.js";

export class kissCELColorPalette extends Format
{
	name           = "KiSS CEL Color Palette";
	ext            = [".kcf"];
	forbidExtMatch = true;
	magic          = ["KiSS CEL color palette", "KISS/GS color"];
	converters     = ["wuimg[format:kcf] -> convert[scale:1200%]"];
}
