import {Format} from "../../Format.js";

export class clarionDatabase extends Format
{
	name        = "Clarion Database File";
	ext         = [".dat"];
	weakExt     = [".dat"];
	magic       = ["Clarion 2 DataBase for DOS"];
	unsupported = true;
	notes       = "Did a Google search, couldn't find anything about it. soffice didn't do anything with it either.";
}
