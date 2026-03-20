import {Format} from "../../Format.js";

export class idesGPC extends Format
{
	name           = "IDES GPC Image";
	ext            = [".gpc"];
	forbidExtMatch = true;
	magic          = ["IDES GPC Image", "image:Adv98.GpcFormat"];
	converters     = ["wuimg[format:gpc]", "GARbro[types:image:Adv98.GpcFormat]"];
}
