import {xu} from "xu";
import {Format} from "../../Format.js";

export class fmTownsSND extends Format
{
	name           = "FM-Towns SND";
	website        = "https://wiki.multimedia.cx/index.php/FM_TOWNS_SND";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["FM-Towns SND"];
	weakMagic      = true;
	converters     = ["vibe2wav[renameOut]"];
}
