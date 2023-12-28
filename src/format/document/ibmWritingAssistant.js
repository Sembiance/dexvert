import {Format} from "../../Format.js";

export class ibmWritingAssistant extends Format
{
	name       = "IBM Writing Assistant";
	website    = "http://fileformats.archiveteam.org/wiki/IBM_Writing_Assistant";
	magic      = ["IBM Writing Assistant document"];
	priority   = this.PRIORITY.LOW;
	converters = ["strings"];
}
