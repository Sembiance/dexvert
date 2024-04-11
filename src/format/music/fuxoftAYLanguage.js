import {Format} from "../../Format.js";

export class fuxoftAYLanguage extends Format
{
	name       = "Fuxoft AY Language";
	website    = "http://fileformats.archiveteam.org/wiki/Fuxoft_AY_Language";
	ext        = [".fxm"];
	magic      = ["Fuxoft AY Language module"];
	converters = ["ayEmul"];
}
