import {Format} from "../../Format.js";

export class mjzArchive extends Format
{
	name           = "MJZ Game Archive";
	ext            = [".mjz"];
	forbidExtMatch = true;
	magic          = [/^geArchive: MJZ_MJZ0(_2)?( |$)/];
	converters     = ["gameextractor[codes:MJZ_MJZ0_2,MJZ_MJZ0]"];
}
