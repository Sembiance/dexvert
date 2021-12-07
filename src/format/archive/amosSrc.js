import {Format} from "../../Format.js";

export class amosSrc extends Format
{
	name       = "AMOS Basic Source Code Archive";
	website    = "http://fileformats.archiveteam.org/wiki/AMOS_BASIC_tokenized_file";
	ext        = [".amos"];
	magic      = ["AMOS Basic source code", "AMOS Pro source"];
	converters = ["listamos & dumpamos"];
}
