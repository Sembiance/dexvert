import {Format} from "../../Format.js";

export class gfaBASICAmiga extends Format
{
	name           = "GFA-BASIC Amiga";
	ext            = [".gfa", ".bas"];
	forbidExtMatch = true;
	magic          = ["GFA-BASIC Amiga"];
	converters     = ["strings"];
}
