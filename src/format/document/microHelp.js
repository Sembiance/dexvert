import {Format} from "../../Format.js";

export class microHelp extends Format
{
	name           = "MicroHelp";
	ext            = [".slb"];
	forbidExtMatch = true;
	magic          = ["MicroHelp Library"];
	converters     = ["strings"];
}
