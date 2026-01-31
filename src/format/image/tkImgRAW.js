import {Format} from "../../Format.js";

export class tkImgRAW extends Format
{
	name           = "TkImg RAW Image";
	website        = "http://fileformats.archiveteam.org/wiki/TkImg_RAW";
	ext            = [".raw"];
	forbidExtMatch = true;
	magic          = ["TkImg RAW bitmap"];
	converters     = ["tkimgConvert"];
}
