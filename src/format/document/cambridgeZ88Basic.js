import {Format} from "../../Format.js";

export class cambridgeZ88Basic extends Format
{
	name           = "Cambridge Z88 Basic";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = ["Cambridge Z88 BASIC tokenized source"];
	converters     = ["strings"];
}
