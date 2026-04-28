import {Format} from "../../Format.js";

export class karlMortonMusic extends Format
{
	name           = "Karl Morton Music";
	ext            = [".mus"];
	forbidExtMatch = true;
	magic          = ["Karl Morton Music format"];
	weakMagic      = true;
	metaProvider   = ["musicInfo"];
	converters     = ["openmpt123"];
}
