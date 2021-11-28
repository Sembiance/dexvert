import {Format} from "../../Format.js";

export class timexHiResGigascreen extends Format
{
	name       = "Timex 2048 Hi-Res Gigascreen";
	website    = "https://zxart.ee/eng/graphics/database/pictureType:timexhrg/sortParameter:date/sortOrder:desc/resultsType:zxitem/";
	ext        = [".hrg"];
	fileSize   = 24578;
	converters = ["recoil2png"];
}
