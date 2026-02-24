import {Format} from "../../Format.js";

export class pakArchive extends Format
{
	name           = "PAK Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PAK_PACK_4( |$)/, /^geArchive: PAK_(37|57)( |$)/];
	converters     = ["gameextractor[codes:PAK_37,PAK_57,PAK_PACK_4]"];
}
