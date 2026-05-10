import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class quakePAK extends Format
{
	name           = "Quake PAK";
	ext            = [".pak"];
	forbidExtMatch = true;
	priority       = this.PRIORITY.LOW;
	magic          = ["Quake archive", "Quake I or II world or extension", /^Archive: PAC?K$/];
	weakMagic      = ["Quake archive"];
	forbiddenMagic = ["Kopftext: 'PACKED'"];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="QDat" && macFileCreator==="Quak") || (macFileType===".pak" && macFileCreator==="HEX2") || (macFileType==="data" && macFileCreator==="Tmb4");
	idCheck        = async inputFile => inputFile.size>12 && (await fileUtil.readFileBytes(inputFile.absolute, 4, 4)).getUInt32LE()<(inputFile.size-4);
	website        = "http://fileformats.archiveteam.org/wiki/Quake_PAK";
	converters     = ["gameextractor"];
}
