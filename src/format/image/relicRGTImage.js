import {Format} from "../../Format.js";

export class relicRGTImage extends Format
{
	name           = "Relic RGT Image";
	ext            = [".rgt"];
	forbidExtMatch = true;
	magic          = [/^geViewer: RGT_RELIC( |$)/];
	weakMagic 	   = true;
	converters     = ["gameextractor[renameOut][codes:RGT_RELIC]"];
}
