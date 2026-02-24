import {Format} from "../../Format.js";

export class simsCompactedResourceFile extends Format
{
	name           = "The Sims Compacted Resource file";
	ext            = [".sims2pack"];
	forbidExtMatch = true;
	magic          = ["The Sims Compacted Resource file", /^geArchive: SIMS2PACK( |$)/];
	converters     = ["gameextractor[codes:SIMS2PACK]"];
}
