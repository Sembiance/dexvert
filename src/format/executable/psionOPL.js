import {Format} from "../../Format.js";

export class psionOPL extends Format
{
	name       = "Psion OPO/OPA Executable";
	website    = "http://fileformats.archiveteam.org/wiki/Psion_OPO/OPA";
	ext        = [".opo", ".opa", ".app"];
	magic      = ["Psion Object/OPL Output", "deark: psionapp (Psion OPO/OPA)"];
	converters = ["deark[module:psionapp][renameOut:false] & strings[matchType:magic]"];
}
