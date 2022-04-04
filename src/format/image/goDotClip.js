import {Format} from "../../Format.js";

export class goDotClip extends Format
{
	name           = "GoDot Clip Image";
	ext            = [".clp"];
	forbidExtMatch = [".clp"];
	magic          = ["GoDot Clip"];
	converters     = ["nconvert", "recoil2png", "view64"];
}
