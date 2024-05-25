import {Format} from "../../Format.js";

export class stc extends Format
{
	name       = "StoneCracker Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StoneCracker";
	ext        = [".stc"];
	magic      = [/^StoneCracker .*compressed$/, /^S\d{3}: StoneCracker/, "SC: StoneCracker", "Archive: StoneCracker"];
	packed     = true;
	converters = ["ancient", "amigadepacker"];
}
