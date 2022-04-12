import {Format} from "../../Format.js";

export class amosMemoryBank extends Format
{
	name           = "AMOS Memory Bank";
	website        = "http://fileformats.archiveteam.org/wiki/AMOS_Memory_Bank";
	ext            = [".abk"];
	forbidExtMatch = true;
	magic          = ["AMOS Memory Bank (generic)", "AMOS Basic memory bank"];
	fallback       = true;
	packed         = true;
	converters     = ["dd[skip:20] -> dexvert"];
}
