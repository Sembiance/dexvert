import {Format} from "../../Format.js";

export class epicITS extends Format
{
	name           = "Epic ITS";
	ext            = [".int"];
	forbidExtMatch = true;
	magic          = ["Epic ITS format"];
	converters     = ["strings"];
}
