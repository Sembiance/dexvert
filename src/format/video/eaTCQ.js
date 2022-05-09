import {Format} from "../../Format.js";

export class eaTCQ extends Format
{
	name         = "Electronic Arts TCQ/TGV Video";
	ext          = [".tgv"];
	magic        = ["Electronic Arts TGQ video", "Electronic Arts TGV video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
