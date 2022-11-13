import {Format} from "../../Format.js";

export class iPerAEH extends Format
{
	name           = "iPer Advanced Embedded Hypertext";
	ext            = [".aeh"];
	forbidExtMatch = true;
	magic          = ["iPer Advanced Embedded Hypertext"];
	converters     = ["foremost"];
}
