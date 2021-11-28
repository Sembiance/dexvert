import {Format} from "../../Format.js";

export class dataShowSprite extends Format
{
	name       = "DataShow Sprite";
	ext        = [".spr"];
	mimeType   = "image/x-datashow-sprite";
	magic      = ["DataShow Sprite"];
	converters = [`abydosconvert[format:${this.mimeType}]`];
}
