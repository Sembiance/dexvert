import {Format} from "../../Format.js";

export class hommAGG2 extends Format
{
	name           = "Heroes of Might & Magic AGG2 archive";
	ext            = [".vol"];
	forbidExtMatch = true;
	magic          = [/^geArchive: AGG_2( |$)/];
	converters     = ["gameextractor[codes:AGG_2]"];
}
