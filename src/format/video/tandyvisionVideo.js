import {Format} from "../../Format.js";

export class tandyvisionVideo extends Format
{
	name           = "Tandyvision Video";
	ext            = [".vid"];
	forbidExtMatch = true;
	magic          = ["Tandyvisionn Video"];
	forbiddenMagic = ["Tandyvisionn Image"];
	converters     = ["na_eofdec[format:tandyvid]"];
}
