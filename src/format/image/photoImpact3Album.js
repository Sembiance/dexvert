import {Format} from "../../Format.js";

export class photoImpact3Album extends Format
{
	name           = "PhotoImpact 3 Album";
	ext            = [".ab3"];
	forbidExtMatch = true;
	magic          = ["PhotoImpact 3 Album"];
	converters     = ["foremost -> rotateImage[degrees:180]"];
}
