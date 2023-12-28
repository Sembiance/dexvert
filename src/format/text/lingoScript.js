import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class lingoScript extends Format
{
	name         = "Lingo Script";
	filename     = [/^lingoScript$/, /^lingoScript_\d+$/];
	magic        = TEXT_MAGIC;
	weakMagic    = true;
	untouched    = true;
	metaProvider = ["text"];
}
