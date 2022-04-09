import {Format} from "../../Format.js";

export class pageSetter extends Format
{
	name           = "PageSetter Document";
	ext            = [".ps"];
	forbidExtMatch = true;
	magic          = ["PageSetter II document"];
	converters     = ["strings"];
}
