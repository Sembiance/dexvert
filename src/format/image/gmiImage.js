import {Format} from "../../Format.js";

export class gmiImage extends Format
{
	name           = "GMI Image";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = [/^geViewer: IMG_GMI( |$)/];
	converters     = ["gameextractor[renameOut][codes:IMG_GMI]"];
}
