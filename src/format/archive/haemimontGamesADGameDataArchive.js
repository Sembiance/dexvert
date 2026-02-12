import {Format} from "../../Format.js";

export class haemimontGamesADGameDataArchive extends Format
{
	name           = "Haemimont Games AD game data archive";
	ext            = [".hpk"];
	forbidExtMatch = true;
	magic          = ["Haemimont Games AD game data archive", /^geArchive: HPK_BPUL( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:HPK_BPUL]"];
}
