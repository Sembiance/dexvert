import {Format} from "../../Format.js";

export class funPhotor extends Format
{
	name           = "Fun Photor";
	ext            = [".fpr"];
	forbidExtMatch = true;
	magic          = ["FunPhotor :fpr:", "funPhotor project/template"];
	converters     = ["nconvert[format:fpr]"];
}
