import {Format} from "../../Format.js";

export class quickBasicTokenizedSource extends Format
{
	name           = "QuickBASIC Tokenized Source";
	ext            = [".bas"];
	forbidExtMatch = true;
	magic          = ["Microsoft QuickBASIC 4.5 tokenized source"];
	converters     = ["strings"];
}
