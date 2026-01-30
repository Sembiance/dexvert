import {Format} from "../../Format.js";

export class idesGPC extends Format
{
	name           = "IDES GPC Image";
	ext            = [".gpc"];
	forbidExtMatch = true;
	magic          = ["IDES GPC Image"];
	converters     = ["wuimg[format:gpc]"];
}
