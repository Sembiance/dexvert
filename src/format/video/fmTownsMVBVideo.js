import {Format} from "../../Format.js";

export class fmTownsMVBVideo extends Format
{
	name           = "FM Towns MVB Video";
	ext            = [".mvb"];
	forbidExtMatch = true;
	magic          = ["FM Towns MVB Video"];
	converters     = ["na_eofdec[format:towns-mvb]"];
}
