import {Format} from "../../Format.js";

export class magixVideo extends Format
{
	name           = "MAGIX Video";
	website        = "http://fileformats.archiveteam.org/wiki/MAGIX_Video";
	ext            = [".mxv"];
	forbidExtMatch = true;
	magic          = ["MAGIX Video"];
	converters     = ["na_eofdec[format:mxv]"];
}
