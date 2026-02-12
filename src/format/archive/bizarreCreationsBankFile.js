import {Format} from "../../Format.js";

export class bizarreCreationsBankFile extends Format
{
	name           = "Bizarre Creations Bank File";
	ext            = [".baf"];
	forbidExtMatch = true;
	magic          = ["BAF (Bizarre Creations Bank File) (baf)", /^geArchive: BAF_BANK( |$)/];
	converters     = ["gameextractor[codes:BAF_BANK]"];
}
