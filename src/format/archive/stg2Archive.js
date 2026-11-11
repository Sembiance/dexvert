import {Format} from "../../Format.js";

export class stg2Archive extends Format
{
	name           = "STG2 Archive";
	ext            = [".stg"];
	forbidExtMatch = true;
	magic          = [/^geArchive: STG_STG2( |$)/];
	converters     = ["gameextractor[codes:STG_STG2]"];
}
