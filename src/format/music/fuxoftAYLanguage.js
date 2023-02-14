import {Format} from "../../Format.js";

export class fuxoftAYLanguage extends Format
{
	name        = "Fuxoft AY Language";
	website     = "http://fileformats.archiveteam.org/wiki/Fuxoft_AY_Language";
	ext         = [".fxm"];
	magic       = ["Fuxoft AY Language module"];
	unsupported = true;
	notes       = `Ay_Emul can play these under linux, but they don't offer a command line conversion option. Source is available (delphi) so I could add support for this feature myself.`;
}
