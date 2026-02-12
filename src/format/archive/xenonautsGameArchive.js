import {Format} from "../../Format.js";

export class xenonautsGameArchive extends Format
{
	name           = "Xenonauts game archive";
	ext            = [".pfp"];
	forbidExtMatch = true;
	magic          = ["Xenonauts game data archive", /^geArchive: PFP_PFPK( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:PFP_PFPK]"];
}
