import {Format} from "../../Format.js";

export class ibmWritingAssistant extends Format
{
	name           = "IBM Writing Assistant";
	magic          = ["IBM Writing Assistant document"];
	converters     = ["strings"];
}
