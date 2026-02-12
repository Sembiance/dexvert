import {Format} from "../../Format.js";

export class lucasArtsGameArchive extends Format
{
	name           = "Lucas Arts Game Archive";
	ext            = [".gob"];
	forbidExtMatch = true;
	magic          = ["LucasArts Game data archive", "Dark Forces Game data archive", "Archive: LucasArts Binary Archive", /^geArchive: GOB_GOB( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="DATA" && ["dRfD", "dRfO", "PPUP"].includes(macFileCreator);
	converters     = ["gameextractor[codes:GOB_GOB]"];
}
