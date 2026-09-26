import {Format} from "../../Format.js";

export class normalitySFX extends Format
{
	name           = "Normality SFX Archive";
	ext            = [".sfx"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SFX_0XFS( |$)/];
	converters     = ["gameextractor[codes:SFX_0XFS]"];
}
