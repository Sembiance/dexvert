import {Format} from "../../Format.js";

export class gfaBASICMSDOS extends Format
{
	name           = "GFA-BASIC MS-DOS";
	ext            = [".gfa", ".bas"];
	forbidExtMatch = true;
	magic          = ["GFA-BASIC MS-DOS"];
	converters     = ["strings"];
}
