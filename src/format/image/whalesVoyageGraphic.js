import {Format} from "../../Format.js";

export class whalesVoyageGraphic extends Format
{
	name           = "Whale's Voyage Graphic";
	ext            = [".brs"];
	forbidExtMatch = true;
	magic          = ["Whale's Voyage graphic"];
	converters     = ["wuimg"];	// ILBM
}
