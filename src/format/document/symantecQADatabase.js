import {Format} from "../../Format.js";

export class symantecQADatabase extends Format
{
	name           = "Symantec Q&A Database File";
	ext            = [".dtf"];
	forbidExtMatch = true;
	magic          = ["Symantec QandA Database File"];
	converters     = ["strings"];
}
