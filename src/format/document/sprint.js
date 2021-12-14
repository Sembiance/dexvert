import {Format} from "../../Format.js";

export class sprint extends Format
{
	name           = "Sprint Document";
	ext            = [".spr"];
	forbidExtMatch = true;
	magic          = ["Sprint document"];
	converters     = ["strings"];
}
