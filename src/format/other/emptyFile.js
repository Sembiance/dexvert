import {Format} from "../../Format.js";

export class emptyFile extends Format
{
	name      = "Empty File";
	magic     = [/^empty$/];
	untouched = true;
}
