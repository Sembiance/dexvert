import {Format} from "../../Format.js";

export class recomposer extends Format
{
	name           = "Recomposer Music File";
	ext            = [".rcp", ".g36"];
	forbidExtMatch = true;
	magic          = ["Recomposer RCP", "Recomposer G36"];
	converters     = ["rcm2smf"];
}
