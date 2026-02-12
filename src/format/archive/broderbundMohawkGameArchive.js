import {Format} from "../../Format.js";

export class broderbundMohawkGameArchive extends Format
{
	name           = "Broderbund Mohawk Game Archive";
	ext            = [".mhk"];
	forbidExtMatch = true;
	magic          = ["Broderbund Mohawk game data archive", "Riven saved game", /^geArchive: MHK_MHWK( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => (macFileType==="MHK_" && macFileCreator==="MoRs") || (macFileType==="LBgP" && macFileCreator==="LBgP");
	converters     = ["gameextractor[codes:MHK_MHWK]"];
}
