import {Format} from "../../Format.js";

export class psionAPP extends Format
{
	name       = "Psion IMG/APP";
	website    = "http://fileformats.archiveteam.org/wiki/Psion_IMG/APP";
	ext        = [".app", ".img"];
	magic      = ["PSION Application/Image executable"];
	converters = ["deark[module:psionapp][renameOut:false] & strings[matchType:magic]"];
}
