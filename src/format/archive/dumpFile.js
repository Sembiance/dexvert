import {Format} from "../../Format.js";

export class dumpFile extends Format
{
	name       = "dump File";
	magic      = ["dump: ", "new-fs dump file", "dump format, "];
	converters = ["restore"];
}
