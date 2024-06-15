import {Format} from "../../Format.js";

export class argonautVideoSequence extends Format
{
	name           = "Argonaut Video Sequence";
	website        = "https://wiki.multimedia.cx/index.php/AVS";
	ext            = [".avs"];
	forbidExtMatch = true;
	magic          = ["Argonaut Video Sequence video"];
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg"];
}
