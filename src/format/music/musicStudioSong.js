import {Format} from "../../Format.js";

export class musicStudioSong extends Format
{
	name       = "Music Studio Song";
	website    = "http://fileformats.archiveteam.org/wiki/The_Music_Studio";
	ext        = [".sng"];
	magic      = ["The Music Studio Song"];		// shared with music/musicStudioSong, so we rely on extension to pick the correct one (and the successful conversion of course)
	converters = ["vibe2mid"];
}
