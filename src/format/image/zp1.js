import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class zp1 extends Format
{
	name       = "ZXpaintyONE";
	website    = "https://web.archive.org/web/20160507112745/http://matt.west.co.tt/demoscene/zxpaintyone/";
	ext        = [".zp1"];
	magic      = TEXT_MAGIC;
	weakMagic  = true;
	converters = ["recoil2png"];
}
