import {Format} from "../../Format.js";

export class aceTexture extends Format
{
	name           = "ACE Texture";
	ext            = [".ace"];
	forbidExtMatch = true;
	magic          = [/^ACE texture (\(compressed\) )?:ace:$/];
	converters     = ["nconvert[format:ace]"];
}
