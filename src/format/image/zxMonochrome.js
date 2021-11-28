import {Format} from "../../Format.js";

export class zxMonochrome extends Format
{
	name       = "ZX Monochrome";
	website    = "https://zxart.ee/eng/graphics/database/pictureType:monochrome/sortParameter:date/sortOrder:desc/resultsType:zxitem/";
	ext        = [".scr"];
	fileSize   = 6144;
	converters = ["recoil2png"];
}
