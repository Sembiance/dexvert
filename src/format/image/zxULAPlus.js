import {Format} from "../../Format.js";

export class zxULAPlus extends Format
{
	name       = "ZX Spectrum ULA+";
	website    = "https://zxart.ee/eng/graphics/database/pictureType:ulaplus/sortParameter:date/sortOrder:desc/resultsType:zxitem/";
	ext        = [".scr"];
	fileSize   = 6976;
	converters = ["recoil2png"];
}
