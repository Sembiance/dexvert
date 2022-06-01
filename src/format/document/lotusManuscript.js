import {Format} from "../../Format.js";

export class lotusManuscript extends Format
{
	name           = "Lotus Manuscript Document";
	ext            = [".doc"];
	forbidExtMatch = true;
	magic          = ["Lotus Manuscript Document"];
	converters     = ["strings"];
}
