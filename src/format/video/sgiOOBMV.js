import {Format} from "../../Format.js";

export class sgiOOBMV extends Format
{
	name           = "SGI OOB MV Video";
	ext            = [".mv", ".mov"];
	forbidExtMatch = true;
	magic          = ["SGI OOB MV"];
	converters     = ["na_eofdec[format:oobmv]"];
}
