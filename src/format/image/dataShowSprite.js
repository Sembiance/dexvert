import {Format} from "../../Format.js";

export class dataShowSprite extends Format
{
	name           = "DataShow Sprite";
	website        = "http://fileformats.archiveteam.org/wiki/DataShow_Sprite";
	ext            = [".spr"];
	forbidExtMatch = true;
	mimeType       = "image/x-datashow-sprite";
	magic          = ["DataShow Sprite"];
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}
