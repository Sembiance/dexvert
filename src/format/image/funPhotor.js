import {Format} from "../../Format.js";

export class funPhotor extends Format
{
	name           = "Fun Photor";
	ext            = [".fpr"];
	forbidExtMatch = true;
	magic          = ["FunPhotor :fpr:"];
	converters     = ["nconvert[format:fpr]"];
}
