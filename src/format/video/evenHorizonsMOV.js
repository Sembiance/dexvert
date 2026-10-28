import {Format} from "../../Format.js";

export class evenHorizonsMOV extends Format
{
	name           = "Even Horizons MOV Video";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["Even Horizons MOV"];
	converters     = ["na_eofdec[format:eh-mov]"];
}
