import {Format} from "../../Format.js";

export class quakePAK extends Format
{
	name           = "Quake PAK";
	ext            = [".pak"];
	forbidExtMatch = true;
	//allowExtMatch  = true;
	magic          = ["Quake archive", "Quake I or II world or extension", /^Archive: PAC?K$/];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="QDat" && macFileCreator==="Quak") || (macFileType===".pak" && macFileCreator==="HEX2") || (macFileType==="data" && macFileCreator==="Tmb4");
	website        = "http://fileformats.archiveteam.org/wiki/Quake_PAK";
	converters     = ["gameextractorCLI"];
}
