import {Format} from "../../Format.js";

export class entisEngineAudio extends Format
{
	name           = "Entis Engine Compressed Audio";
	ext            = [".mio"];
	forbidExtMatch = true;
	magic          = ["audio:Entis.MioAudio", "vgmstream: mio"];
	weakMagic      = true;
	converters     = ["vgmstream[types:mio]", "GARbro[types:audio:Entis.MioAudio]"];
}
