import {Format} from "../../Format.js";

export class clarisWorks extends Format
{
	name           = "ClarisWorks/AppleWorks Document";
	website        = "http://fileformats.archiveteam.org/wiki/ClarisWorks";
	ext            = [".cwk", ".cws"];
	forbidExtMatch = true;
	magic          = [/AppleWorks\/ClarisWorks .+Document/, "Claris Works document", "AppleWorks CWK Document", /^fmt\/(736|737|738|739|740|741|742|743|744|747|748|749|750|752|845|846|847|849)( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => ["CWDB", "CWGR", "CWPT", "CWSS", "CWWP", "lCLW", "sWGR", "sWWP"].includes(macFileType) && macFileCreator==="BOBO";
	converters     = ["soffice[format:ClarisWorks]", "soffice[format:ClarisWorks_Calc]", "soffice[format:ClarisWorks_Draw]", "soffice[format:ClarisWorks_Impress]", "soffice[format:Claris_Resolve_Calc]", "mwaw2text"];
	notes          = "Foreign language ClarisWorks files like 差込データ don't convert well at all. There is a version of ClarisWorks available for windows, so I could try using that to help convert clarisworks files.";
}
