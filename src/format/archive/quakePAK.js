import {Format} from "../../Format.js";

export class quakePAK extends Format
{
	name           = "Quake PAK";
	ext            = [".pak"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;
	magic          = ["Quake archive", "Quake I or II world or extension", /^Archive: PAC?K$/];
	forbiddenMagic = ["Kopftext: 'PACKED'"];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="QDat" && macFileCreator==="Quak") || (macFileType===".pak" && macFileCreator==="HEX2") || (macFileType==="data" && macFileCreator==="Tmb4");
	website        = "http://fileformats.archiveteam.org/wiki/Quake_PAK";
	converters     = ["gameextractor"];
}
