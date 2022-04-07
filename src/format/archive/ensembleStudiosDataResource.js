import {Format} from "../../Format.js";

export class ensembleStudiosDataResource extends Format
{
	name       = "Ensemble Studios Data Resource";
	ext        = [".drs"];
	magic      = ["Ensemble Studios Data Resource"];
	converters = ["gameextractor"];
}
