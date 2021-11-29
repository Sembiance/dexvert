import {Format} from "../../Format.js";

export class gfaBasicWindows extends Format
{
	name           = "GFA-BASIC Windows";
	ext            = [".gfw"];
	forbidExtMatch = true;
	magic          = ["GFA-BASIC Windows v3 tokenized source"];
	converters     = ["strings"];
}
