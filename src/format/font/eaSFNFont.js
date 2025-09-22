import {Format} from "../../Format.js";

export class eaSFNFont extends Format
{
	name           = "EA SFN Font";
	ext            = [".sfn"];
	forbidExtMatch = true;
	magic          = ["EA SFN Font"];
	converters     = ["wuimg"];
}
