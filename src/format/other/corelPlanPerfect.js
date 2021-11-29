import {Format} from "../../Format.js";

export class corelPlanPerfect extends Format
{
	name           = "Corel Plan Perfect";
	ext            = [".pln"];
	forbidExtMatch = true;
	magic          = ["Corel Plan Perfect"];
	converters     = ["strings"];
}
