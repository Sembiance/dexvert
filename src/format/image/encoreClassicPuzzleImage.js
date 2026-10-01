import {Format} from "../../Format.js";

export class encoreClassicPuzzleImage extends Format
{
	name           = "Encore Classic Puzzle Image";
	ext            = [".tex"];
	forbidExtMatch = true;
	magic          = [/^geViewer: ZIP_PK_TEX_TEXL001( |$)/];
	keepFilename   = true;
	weakMagic      = true;
	converters     = ["gameextractor[renameOut][codes:ZIP_PK_TEX_TEXL001][skipVerify]"];
}
