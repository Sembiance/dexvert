import {Format} from "../../Format.js";

export class comancheVideoDataArchive extends Format
{
	name           = "Comanche Video Data archive";
	ext            = [".kdv"];
	forbidExtMatch = true;
	magic          = ["Comanche Video Data archive", /^geArchive: KDV_KRL0( |$)/];
	converters     = ["gameextractor[codes:KDV_KRL0]"];
}
