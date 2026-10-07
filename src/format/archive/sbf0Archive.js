import {Format} from "../../Format.js";

export class sbf0Archive extends Format
{
	name           = "SBF0 Archive";
	ext            = [".sbf"];
	forbidExtMatch = true;
	magic          = [/^geArchive: SBF_SBF0( |$)/];
	converters     = ["gameextractor[codes:SBF_SBF0]"];
}
