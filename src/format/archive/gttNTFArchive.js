import {Format} from "../../Format.js";

export class gttNTFArchive extends Format
{
	name           = "GTT NTF Archive";
	ext            = [".dxt", ".gtt"];
	forbidExtMatch = true;
	magic          = [/^geArchive: GTT_NTF( |$)/];
	converters     = ["gameextractor[codes:GTT_NTF]"];
}
