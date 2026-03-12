import {Format} from "../../Format.js";

export class sacredPAK extends Format
{
	name           = "Sacred PAK Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [/^geArchive: PAK_TEX( |$)/];
	converters     = ["gameextractor[codes:PAK_TEX]"];
}
