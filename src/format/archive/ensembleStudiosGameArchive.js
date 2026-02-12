import {Format} from "../../Format.js";

export class ensembleStudiosGameArchive extends Format
{
	name           = "Ensemble Studios Game Archive";
	ext            = [".drs"];
	forbidExtMatch = true;
	magic          = ["Ensemble Studios Data Resource", /^geArchive: (DRS|DRS_3)( |$)/];
	converters     = ["gameextractor[codes:DRS,DRS_3]"];
}
