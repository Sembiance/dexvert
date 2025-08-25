import {Format} from "../../Format.js";

export class totalAnnihilationGAF extends Format
{
	name           = "Total Annihilation GAF Image";
	ext            = [".gaf"];
	forbidExtMatch = true;
	magic          = ["Total Annihilation :gaf:"];
	converters     = ["nconvert[format:gaf]"];
}
