import {Format} from "../../Format.js";

export class capcomARC extends Format
{
	name           = "Capcom ARC game archive";
	ext            = [".arc"];
	forbidExtMatch = true;
	magic          = [/^geArchive: ARC_ARC_2( |$)/];
	converters     = ["gameextractor[codes:ARC_ARC_2]"];
}
