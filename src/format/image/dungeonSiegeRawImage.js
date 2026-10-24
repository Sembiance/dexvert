import {Format} from "../../Format.js";

export class dungeonSiegeRawImage extends Format
{
	name           = "Dungeon Siege Raw Image";
	ext            = [".raw"];
	forbidExtMatch = true;
	magic          = [/^geViewer: DSRES_DSIGTANK_RAW( |$)/];
	converters     = ["gameextractor[renameOut][codes:DSRES_DSIGTANK_RAW]"];
}
