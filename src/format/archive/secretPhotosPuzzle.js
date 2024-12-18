import {Format} from "../../Format.js";

export class secretPhotosPuzzle extends Format
{
	name           = "Secret Photos puzzle";
	ext            = [".xp0"];
	forbidExtMatch = true;
	magic          = ["Secret Photos puzzle"];
	weakMagic      = true;
	converters     = ["foremost"];
}
