import {Format} from "../../Format.js";

export class uleadTexture extends Format
{
	name           = "Ulead Image";
	ext            = [".pe4"];
	forbidExtMatch = true;
	magic          = ["Ulead Texture :upe4:"];
	converters     = ["nconvert[format:upe4]"];
}
