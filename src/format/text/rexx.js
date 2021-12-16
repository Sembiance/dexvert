import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class rexx extends Format
{
	name           = "OS/2 REXX Batch file";
	website        = "https://www.tutorialspoint.com/rexx/index.htm";
	ext            = [".cmd", ".rexx", ".rex"];
	forbidExtMatch = true;
	magic          = ["OS/2 REXX batch file", ...TEXT_MAGIC];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
