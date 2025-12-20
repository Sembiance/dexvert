import {Format} from "../../Format.js";

export class emptyFile extends Format
{
	name      = "Empty File";
	magic     = [/^empty$/, "Format: Empty file"];
	untouched = true;
}
