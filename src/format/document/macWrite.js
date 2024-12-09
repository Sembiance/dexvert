import {Format} from "../../Format.js";

export class macWrite extends Format
{
	name           = "MacWrite Document";
	website        = "http://fileformats.archiveteam.org/wiki/MacWrite";
	ext            = [".mcw", ".doc"];
	forbidExtMatch = true;
	magic          = [/^MacWrite .*[Dd]ocument/];
	idMeta         = ({macFileType, macFileCreator}) => ["MW2D", "MW2S"].includes(macFileType) && ["MSWD", "MWII"].includes(macFileCreator);
	converters     = ["soffice[format:MacWrite]", "wordForWord"];
}
