import {Format} from "../../Format.js";

export class stFaxScript extends Format
{
	name           = "STFax Script";
	ext            = [".script"];
	forbidExtMatch = true;
	magic          = ["STFax Script"];
	converters     = ["strings"];
}
