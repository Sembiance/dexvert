import {Format} from "../../Format.js";

export class stc extends Format
{
	name       = "StoneCracker Archive";
	website    = "http://fileformats.archiveteam.org/wiki/StoneCracker";
	ext        = [".stc"];
	magic      = [/^StoneCracker .*compressed$/];
	converters = ["amigadepacker"];
}
