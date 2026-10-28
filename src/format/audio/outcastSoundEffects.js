import {Format} from "../../Format.js";

export class outcastSoundEffects extends Format
{
	name           = "Outcast Sound effects";
	website        = "https://playtechs.blogspot.com/2010/05/reading-outcast-sfx-files.html";
	ext            = [".sfx"];
	forbidExtMatch = true;
	magic          = ["Outcast Sound effects"];
	converters     = ["vibe2wav[renameOut]"];
}

