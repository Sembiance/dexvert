import {Format} from "../../Format.js";

export class duckIVF extends Format
{
	name           = "Duck IVF Video";
	website        = "https://wiki.multimedia.cx/index.php/Duck_IVF";
	ext            = [".ivf"];
	forbidExtMatch = true;
	magic          = ["IVF Video", "IVF VP8 Video", "On2 IVF (ivf)", "Format: Duck IVF", /^Duck IVF video file/];
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg[format:ivf]"];
}
