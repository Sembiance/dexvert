import {Format} from "../../Format.js";

export class hsMovie extends Format
{
	name           = "HsMovie";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["HsMovie"];
	converters     = ["na_eofdec[format:hsmovie]"];
}
