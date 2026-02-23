import {Format} from "../../Format.js";

export class opkPAK extends Format
{
	name           = "OPK PAK";
	ext            = [".osp", ".ovp", ".obp"];
	forbidExtMatch = true;
	magic          = [/^geArchive: OPK_PAK( |$)/];
	converters     = ["gameextractor[codes:OPK_PAK]"];
}
