import {Format} from "../../Format.js";

export class mallTycoonGameDataArchive extends Format
{
	name           = "Mall Tycoon game data archive";
	ext            = [".muk"];
	forbidExtMatch = true;
	magic          = ["Mall Tycoon game data archive", /^geArchive: MUK_MUKFILE_2( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:MUK_MUKFILE_2]"];
}
