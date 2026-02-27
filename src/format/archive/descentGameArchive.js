import {Format} from "../../Format.js";

export class descentGameArchive extends Format
{
	name           = "Descent Game Archive";
	ext            = [".hog"];
	forbidExtMatch = true;
	magic          = ["Descent game data archive", /^geArchive: HOG_DHF( |$)/, "dragon: HOG "];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="HOG " && ["DCNT", "DCT2"].includes(macFileCreator);
	converters     = ["gameextractor[codes:HOG_DHF]", "dragonUnpacker[types:HOG]", "gamearch"];
}
