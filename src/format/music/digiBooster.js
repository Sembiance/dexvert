import {Format} from "../../Format.js";

export class digiBooster extends Format
{
	name         = "DigiBooster Module";
	website      = "http://fileformats.archiveteam.org/wiki/DigiBooster_v1.x_module";
	ext          = [".digi", ".dbm"];
	magic        = ["DIGIBooster module", "DIGI Booster module", "DIGI Booster Pro Module", "DigiBoosterPro module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123", "xmp", "openmpt123", "zxtune123"];
}
