import {Format} from "../../Format.js";

export class musicStudioSong extends Format
{
	name       = "Music Studio Song";
	website    = "http://fileformats.archiveteam.org/wiki/The_Music_Studio";
	ext        = [".sng"];
	magic      = ["The Music Studio Song"];
	converters = ["vibe2mid"];
}
