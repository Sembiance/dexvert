import {Format} from "../../Format.js";

export class goDotClip extends Format
{
	name           = "GoDot Clip Image";
	ext            = [".clp"];
	forbidExtMatch = [".clp"];
	magic          = ["GoDot Clip", "GoDot clip :god:"];
	converters     = ["nconvert[format:god]", "recoil2png[format:CLP.GodotClp]", "view64"];
}
