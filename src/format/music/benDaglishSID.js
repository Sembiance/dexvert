import {xu} from "xu";
import {Format} from "../../Format.js";

export class benDaglishSID extends Format
{
	name       = "Ben Daglish SID";
	website    = "http://fileformats.archiveteam.org/wiki/Ben_Daglish_SID";
	ext        = [".bds"];
	magic      = ["Benn Daglish SID chiptune"];
	converters = ["uade123"];
}
