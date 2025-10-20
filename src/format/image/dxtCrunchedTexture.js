import {Format} from "../../Format.js";

export class dxtCrunchedTexture extends Format
{
	name           = "DXT Crunched Texture";
	ext            = [".res", ".crn"];
	forbidExtMatch = true;
	safeExt        = ".crn";
	magic          = [/^Crunch compressed texture:/];
	classify       = true;
	converters     = ["crunchDXT"];
}
