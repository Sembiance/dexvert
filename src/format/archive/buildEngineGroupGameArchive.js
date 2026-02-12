import {Format} from "../../Format.js";

export class buildEngineGroupGameArchive extends Format
{
	name           = "Build Engine Group Game Archive";
	website        = "http://fileformats.archiveteam.org/wiki/GRP_(Duke_Nukem_3D)";
	ext            = [".grp", ".dat"];
	forbidExtMatch = true;
	magic          = ["Build engine group file", "Build Engine GRP container", /^geArchive: GRP_KEN( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="data" && ["Duke", "ShdW"].includes(macFileCreator);
	converters     = ["gameextractor[codes:GRP_KEN]", "gamearch"];
}
