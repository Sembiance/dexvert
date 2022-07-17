import {Format} from "../../Format.js";

export class actWordProcessorDocument extends Format
{
	name           = "ACT! Word Processor Document";
	ext            = [".wpa"];
	forbidExtMatch = true;
	magic          = ["ACT! word processor document"];
	converters     = ["strings"];
}
