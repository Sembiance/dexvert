import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class binHex extends Format
{
	name       = "BinHex";
	website    = "http://fileformats.archiveteam.org/wiki/BinHex";
	ext        = [".hqx", ".hcx", ".hex"];
	magic      = [/^x-fmt\/416( |$)/, ...TEXT_MAGIC];
	weakMagic  = TEXT_MAGIC;
	converters = ["unar", "deark"];
}
