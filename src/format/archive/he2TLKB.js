import {Format} from "../../Format.js";

export class he2TLKB extends Format
{
	name           = "HE2 TLKB Archive";
	ext            = [".he2", ".he4"];
	forbidExtMatch = true;
	magic          = [/^geArchive: HE2_TLKB( |$)/];
	converters     = ["gameextractor[codes:HE2_TLKB]"];
}
