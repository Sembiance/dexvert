import {Format} from "../../Format.js";

export class doomMUS extends Format
{
	name           = "DMX Doom/Heretic Music";
	website        = "http://fileformats.archiveteam.org/wiki/Doom_MUS";
	ext            = [".mus"];
	forbidExtMatch = true;
	safeExt        = ".mus";
	magic          = ["Doom/Heretic music"];
	converters     = ["mus2mid", "midistar2mp3", "doomMUS2mp3"];
}
