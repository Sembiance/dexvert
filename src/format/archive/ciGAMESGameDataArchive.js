import {Format} from "../../Format.js";

export class ciGAMESGameDataArchive extends Format
{
	name           = "CI GAMES game data archive";
	ext            = [".dpk"];
	forbidExtMatch = true;
	magic          = ["CI GAMES game data archive", /^geArchive: DPK_DPK4( |$)/];
	weakMagic      = true;
	converters     = ["gameextractor[codes:DPK_DPK4]"];
}
