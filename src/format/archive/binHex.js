import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class binHex extends Format
{
	name       = "BinHex";
	website    = "http://fileformats.archiveteam.org/wiki/BinHex";
	ext        = [".hqx", ".hcx", ".hex"];
	magic      = ["BinHex binary text", "BinHex encoded", "HQX Archiv gefunden", "application/mac-binhex40", /^BinHex \d\.\d encoded/, /^BinHex$/, /^x-fmt\/416( |$)/, ...TEXT_MAGIC];
	weakMagic  = TEXT_MAGIC;
	converters = ["unar", "deark[module:binhex]"];
}
