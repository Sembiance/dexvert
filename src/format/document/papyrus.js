import {Format} from "../../Format.js";

export class papyrus extends Format
{
	name           = "Papyrus";
	ext            = [".pap"];
	forbidExtMatch = true;
	magic          = ["Papyrus document"];
	converters     = ["strings"];
}
