import {Format} from "../../Format.js";

export class mobildDBDatabase extends Format
{
	name           = "Palm MobileDB Database";
	ext            = [".pdb"];
	forbidExtMatch = true;
	magic          = ["MobileDB PalmOS document", "Palm MobileDB database"];
	converters     = ["pdb2csv"];
}
