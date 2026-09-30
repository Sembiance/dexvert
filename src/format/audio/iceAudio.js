import {Format} from "../../Format.js";

export class iceAudio extends Format
{
	name           = "IceAudio";
	ext            = [".cr"];
	forbidExtMatch = true;
	magic          = ["audio:Ice.IceAudio"];
	weakMagic      = true;
	converters     = ["GARbro[types:audio:Ice.IceAudio]"];
}
