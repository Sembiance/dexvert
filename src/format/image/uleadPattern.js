import {Format} from "../../Format.js";

export class uleadPattern extends Format
{
	name           = "Ulead Pattern";
	ext            = [".pst"];
	forbidExtMatch = true;
	magic          = ["Ulead Pattern :upst:"];
	converters     = ["nconvert[format:upst]"];
}
