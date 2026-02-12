import {Format} from "../../Format.js";

export class hooligansGameDataArchive extends Format
{
	name           = "Hooligans game data archive";
	ext            = [".x13"];
	forbidExtMatch = true;
	magic          = ["Hooligans game data archive", /^geArchive: PAK_PACK( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:PAK_PACK]"];
}
