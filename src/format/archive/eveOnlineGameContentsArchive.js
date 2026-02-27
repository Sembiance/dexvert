import {Format} from "../../Format.js";

export class eveOnlineGameContentsArchive extends Format
{
	name           = "EVE Online Game Contents archive";
	ext            = [".stuff"];
	forbidExtMatch = true;
	magic          = ["EVE Online Game Contents archive", /^geArchive: STUFF( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:STUFF]"];
}
