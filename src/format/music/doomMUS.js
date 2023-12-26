import {Format} from "../../Format.js";

export class doomMUS extends Format
{
	name           = "Doom/Heretic Music";
	website        = "http://fileformats.archiveteam.org/wiki/Doom_MUS";
	ext            = [".mus"];
	forbidExtMatch = true;
	magic          = ["Doom/Heretic music"];
	converters     = ["mus2mid", "doomMUS2mp3"];
}
