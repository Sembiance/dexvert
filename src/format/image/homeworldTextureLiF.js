import {Format} from "../../Format.js";

export class homeworldTextureLiF extends Format
{
	name           = "Homeworld Texture LiF";
	ext            = [".lif"];
	forbidExtMatch = true;
	magic          = ["Homeworld Texture :lif:", "Homeworld Library Image Format image/texture"];
	converters     = ["nconvert[format:lif]"];
}
