import {Format} from "../../Format.js";

export class db2Bind extends Format
{
	name           = "DB2 Bind";
	ext            = [".bnd"];
	forbidExtMatch = true;
	magic          = ["DB2 Bind"];
	converters     = ["strings"];
}
