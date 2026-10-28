import {Format} from "../../Format.js";

export class mioCompressedAudio extends Format
{
	name           = "MIO compressed audio";
	ext            = [".mio"];
	forbidExtMatch = true;
	magic          = ["MIO compressed audio"];
	converters     = ["vibe2wav[renameOut]"];
}
