import {Format} from "../../Format.js";

export class reunionGraphic extends Format
{
	name           = "Reunion Graphic";
	ext            = [".pic"];
	forbidExtMatch = true;
	magic          = ["Reunion graphics"];
	converters     = ["wuimg"];
}
