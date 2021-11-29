import {Format} from "../../Format.js";

export class dBaseLabelDesign extends Format
{
	name           = "dBase Label Design";
	ext            = [".lbl"];
	forbidExtMatch = true;
	magic          = ["dBASE IV Label design"];
	converters     = ["strings"];
}
