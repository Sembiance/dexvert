import {Format} from "../../Format.js";

export class clarionDatabase extends Format
{
	name           = "Clarion Database File";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Clarion 2 DataBase for DOS"];
	unsupported    = true;	// 5,548 unique files on discmaster, but just decided to pass on vibe coding a converter for now
	notes          = "Did a Google search, couldn't find anything about it. soffice didn't do anything with it either.";
}
