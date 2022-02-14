import {Format} from "../../Format.js";

export class clarionMemo extends Format
{
	name           = "Clarion Memo";
	ext            = [".mem"];
	forbidExtMatch = true;
	magic          = ["Clarion Developer (v2 and above) memo data"];
	converters     = ["strings"];
}
