import {Format} from "../../Format.js";

export class chasmGameArchive extends Format
{
	name           = "Chasm Game Archive";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = ["Chasm BIN archive", /^geArchive: BIN_CSID( |$)/];
	converters     = ["gameextractor[codes:BIN_CSID]"];
}
