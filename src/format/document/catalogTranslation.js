import {Format} from "../../Format.js";

export class catalogTranslation extends Format
{
	name           = "Amiga Catalog Translation file";
	ext            = [".ct"];
	forbidExtMatch = true;
	magic          = ["catalog translation"];
	converters     = ["strings"];
}
