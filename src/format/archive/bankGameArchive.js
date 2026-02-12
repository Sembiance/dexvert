import {Format} from "../../Format.js";

export class bankGameArchive extends Format
{
	name           = "Bank Game Archive";
	ext            = [".bnk", ".-0"];
	forbidExtMatch = true;
	magic          = ["Bank game data archive", /^geArchive: 0( |$)/];
	converters     = ["gameextractor[codes:0]"];
}
