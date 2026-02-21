import {Format} from "../../Format.js";

export class gcfGameArchive extends Format
{
	name           = "GCF Game Archive";
	ext            = [".gcf"];
	forbidExtMatch = true;
	magic          = [/^geArchive: (GCF|GCF_1|GCF_2)( |$)/];
	converters     = ["gameextractor[codes:GCF,GCF_1,GCF_2]"];
}
