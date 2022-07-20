import {Format} from "../../Format.js";

export class deScribe extends Format
{
	name           = "DeScribe Document";
	ext            = [".doc", ".des"];
	forbidExtMatch = true;
	magic          = ["DeScribe document"];
	converters     = ["strings"];
}
