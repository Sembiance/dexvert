import {Format} from "../../Format.js";

export class hiJaakVectorGraphic extends Format
{
	name           = "HiJaak Vector Graphic";
	ext            = [".pdw"];
	forbidExtMatch = true;
	magic          = ["HiJaak vector graphics"];
	converters     = ["hiJaakExpress"];
}
