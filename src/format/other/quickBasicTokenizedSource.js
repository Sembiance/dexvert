import {Format} from "../../Format.js";

export class quickBasicTokenizedSource extends Format
{
	name           = "QuickBASIC Tokenized Source";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = [/^Microsoft QuickBASIC \d\.\d tokenized source$/, /^QuickBASIC Extended .*Source$/];
	converters     = ["strings"];
}
