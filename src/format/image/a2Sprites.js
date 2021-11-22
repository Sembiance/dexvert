import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class a2Sprites extends Format
{
	name       = "Apple II Sprites";
	ext        = [".spr"];
	magic      = TEXT_MAGIC;
	weakMagic  = true;
	converters = ["recoil2png"]
}
