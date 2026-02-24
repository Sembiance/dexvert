import {Format} from "../../Format.js";

export class drakanOrderOfTheFlameSavedGame extends Format
{
	name           = "Drakan: Order Of The Flame Saved Game";
	ext            = [".rsg", ".rlt"];
	forbidExtMatch = true;
	magic          = ["Drakan: Order Of The Flame Saved Game", /^geArchive: SDU_SRSC( |$)/];
	converters     = ["gameextractor[codes:SDU_SRSC]"];
}
