import {Format} from "../../Format.js";

export class locomotiveBASIC extends Format
{
	name           = "Locomotive BASIC";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = ["Amstrad CPC Locomotive BASIC tokenized source"];
	converters     = ["strings"];
}
