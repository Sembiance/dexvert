import {Format} from "../../Format.js";

export class whalesVoyageGraphic extends Format
{
	name           = "Whale's Voyage Graphic";
	ext            = [".brs"];
	forbidExtMatch = true;
	magic          = ["Whale's Voyage graphic"];
	converters     = ["deark[module:wv_brs][renameOut] -> dexvert[asFormat:image/iffILBM]", "wuimg[format:ilbm]"];
}
