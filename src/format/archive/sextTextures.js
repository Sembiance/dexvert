import {Format} from "../../Format.js";

export class sextTextures extends Format
{
	name           = "SEXT Textures";
	ext            = [".textures"];
	forbidExtMatch = true;
	magic          = [/^geArchive: TEXTURES_SXET( |$)/];
	converters     = ["gameextractor[codes:TEXTURES_SXET]"];
}
