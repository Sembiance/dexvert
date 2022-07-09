import {Format} from "../../Format.js";

export class eaTCQ extends Format
{
	name         = "Electronic Arts TCQ/TGV Video";
	website      = "https://wiki.multimedia.cx/index.php/Electronic_Arts_TGV";
	ext          = [".tgv"];
	magic        = ["Electronic Arts TGQ video", "Electronic Arts TGV video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
