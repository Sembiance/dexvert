import {Format} from "../../Format.js";

export class lucasArtsGameArchive extends Format
{
	name           = "Lucas Arts Game Archive";
	ext            = [".gob", "lab"];
	forbidExtMatch = true;
	magic          = ["LucasArts Game data archive", "Dark Forces Game data archive", "Archive: LucasArts Binary Archive", /^geArchive: (GOB_GOB_2|GOB_GOB|LAB_LABN|M4B_LABN)( |$)/, "dragon: DGOB ", "dragon: GOB "];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="DATA" && ["dRfD", "dRfO", "PPUP"].includes(macFileCreator);
	converters     = ["gameextractor[codes:GOB_GOB_2,GOB_GOB,LAB_LABN,M4B_LABN]", "dragonUnpacker[types:DGOB]", "dragonUnpacker[types:GOB]"];
}
