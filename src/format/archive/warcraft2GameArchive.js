import {Format} from "../../Format.js";

export class warcraft2GameArchive extends Format
{
	name           = "Warcraft 2 Game Archive";
	ext            = [".war"];
	forbidExtMatch = true;
	magic          = ["Warcraft game data archive", /^geArchive: WAR( |$)/];
	weakMagic      = true;
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="W2df" && macFileCreator==="W2dm";
	converters     = ["gameextractor[codes:WAR]"];
}
