import {Format} from "../../Format.js";

export class clarisWorksDatabase extends Format
{
	name           = "ClarisWorks Database";
	website        = "http://fileformats.archiveteam.org/wiki/ClarisWorks";
	ext            = [".db"];
	forbidExtMatch = true;
	magic          = [/^fmt\/848( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="sWDB" && macFileCreator==="BOBO";
	converters     = ["soffice[matchType:magic]", "mwaw2text"];
}
