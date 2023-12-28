import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class zp1 extends Format
{
	name       = "ZXpaintyONE";
	website    = "http://fileformats.archiveteam.org/wiki/ZXpaintyONE";
	ext        = [".zp1"];
	magic      = TEXT_MAGIC;
	weakMagic  = true;
	converters = ["recoil2png"];
}
