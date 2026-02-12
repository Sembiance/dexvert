import {Format} from "../../Format.js";

export class creativeAssemblyGameResourceData extends Format
{
	name           = "Creative Assembly game resource data";
	ext            = [".pack"];
	forbidExtMatch = true;
	magic          = ["Creative Assembly game resource data", /^geArchive: PACK_PFH0( |$)/];
	converters     = ["gameextractor[codes:PACK_PFH0]"];
}
