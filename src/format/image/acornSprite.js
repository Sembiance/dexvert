import {Format} from "../../Format.js";

export class acornSprite extends Format
{
	name       = "Acorn (RISC OS) Sprite";
	website    = "http://fileformats.archiveteam.org/wiki/Acorn_Sprite";
	ext        = [".acorn"];
	magic      = ["GLS_BINARY_LSB_FIRST", "GLS_BINARY_MSB_FIRST"];
	priority   = this.PRIORITY.LOW;
	converters = ["deark[module:rosprite]", "nconvert"];
}
