import {Format} from "../../Format.js";

export class vueDEspritVOB extends Format
{
	name           = "Vue D'Esprit VOB";
	ext            = [".vob", ".mat"];
	forbidExtMatch = true;
	magic          = ["Vue d'Esprit :vob:"];
	converters     = ["nconvert[format:vob]"];
}
