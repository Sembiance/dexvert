import {Format} from "../../Format.js";

export class fastSprSprite extends Format
{
	name         = "FastSpr Sprite";
	website      = "http://fileformats.archiveteam.org/wiki/FastSpr_sprite_file";
	magic        = ["FastSpr sprite"];
	skipClassify = true;
	converters   = ["nobrainer"];
}
