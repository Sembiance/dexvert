import {Format} from "../../Format.js";

export class videoToasterRTV extends Format
{
	name           = "Video Toaster RTV Video";
	ext            = [".rtv"];
	forbidExtMatch = true;
	magic          = ["Video Toaster RTV"];
	converters     = ["na_eofdec[format:vtoaster-rtv]"];
}
