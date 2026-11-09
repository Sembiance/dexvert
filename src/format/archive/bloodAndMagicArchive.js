import {Format} from "../../Format.js";

export class bloodAndMagicArchive extends Format
{
	name           = "Blood & Magic archive";
	ext            = [".stf"];
	forbidExtMatch = true;
	magic          = [/^geArchive: STF( |$)/];
	converters     = ["gameextractor[codes:STF]"];
}
