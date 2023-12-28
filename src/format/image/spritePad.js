import {Format} from "../../Format.js";

export class spritePad extends Format
{
	name       = "SpritePad";
	website    = "http://fileformats.archiveteam.org/wiki/SpritePad";
	ext        = [".spd"];
	magic      = ["Sprite Pad Data", /^fmt\/1561( |$)/];
	converters = ["recoil2png", "view64"];
}
