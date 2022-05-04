import {Format} from "../../Format.js";

export class spritePad extends Format
{
	name       = "SpritePad";
	website    = "http://www.subchristsoftware.com/spritepadfree/index.htm";
	ext        = [".spd"];
	magic      = ["Sprite Pad Data", /^fmt\/1561( |$)/];
	converters = ["recoil2png", "view64"];
}
