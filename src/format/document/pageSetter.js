import {Format} from "../../Format.js";

export class pageSetter extends Format
{
	name           = "PageSetter Document";
	ext            = [".ps"];
	forbidExtMatch = true;
	magic          = [/^PageSetter I{0,3} ?document/];
	converters     = ["strings"];
}
