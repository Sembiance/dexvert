import {Format} from "../../Format.js";

export class secretPhotosPuzzle extends Format
{
	name           = "Secret Photos puzzle";
	website        = "http://fileformats.archiveteam.org/wiki/Secret_Photos_puzzle";
	ext            = [".xp0"];
	forbidExtMatch = true;
	magic          = ["Secret Photos puzzle"];
	weakMagic      = true;
	converters     = ["foremost"];
}
