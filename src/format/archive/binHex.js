import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class binHex extends Format
{
	name       = "BinHex";
	website    = "http://fileformats.archiveteam.org/wiki/BinHex";
	ext        = [".hqx", ".hcx", ".hex"];
	magic      = TEXT_MAGIC;
	weakMagic  = true;
	converters = ["unar", "deark"];
}
