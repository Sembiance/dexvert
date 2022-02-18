import {Format} from "../../Format.js";

export class acornReplayVideo extends Format
{
	name         = "Acorn Replay Video";
	website      = "http://fileformats.archiveteam.org/wiki/Acorn_Replay";
	ext          = [".rpl"];
	magic        = ["ARMovie"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:rpl]"];
}
