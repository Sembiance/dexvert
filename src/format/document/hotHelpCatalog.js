import {Format} from "../../Format.js";

export class hotHelpCatalog extends Format
{
	name           = "HotHelp Catalog";
	ext            = [".cat"];
	forbidExtMatch = true;
	magic          = ["HotHelp Catalog"];
	converters     = ["strings"];
}
