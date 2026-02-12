import {Format} from "../../Format.js";

export class novalogicGameArchive extends Format
{
	name           = "Novalogic Game Archive";
	ext            = [".pff"];
	forbidExtMatch = true;
	magic          = ["Novalogic game data archive", /^geArchive: (PFF_PFF3_2|PFF_PFF3|PFF)( |$)/];
	converters     = ["gameextractor[codes:PFF_PFF3_2,PFF_PFF3,PFF]"];
}
