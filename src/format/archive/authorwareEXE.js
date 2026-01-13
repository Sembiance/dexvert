import {Format} from "../../Format.js";

export class authorwareEXE extends Format
{
	name           = "Authorware Wrapped EXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["AuthorwareEXE"];
	converters     = ["exeUnPostContent[idstring:PCRS][ext:.app]"];	// probably more idstrings possible
}
