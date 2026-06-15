import {Format} from "../../Format.js";
import {_MOV_MAGIC} from "../video/mov.js";

export class twvAudio extends Format
{
	name           = "TWV Audio";
	ext            = [".twv"];
	forbidExtMatch = true;
	magic          = _MOV_MAGIC;
	weakMagic      = true;
	converters     = ["vibe2wav[singleFile][renameOut]"];
}
