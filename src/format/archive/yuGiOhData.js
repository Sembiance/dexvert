import {Format} from "../../Format.js";

export class yuGiOhData extends Format
{
	name           = "Yu Gi Oh! data";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Yu Gi Oh! data"];
	unsupported    = true;
	notes          = "Extractor could be written, see: https://yugiohextractor.sourceforge.net/documentation.htm";
}
