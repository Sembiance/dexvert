import {Format} from "../../Format.js";

export class bitmapBrothersJV extends Format
{
	name         = "Bitmap Brotehrs JV Video";
	website      = "https://wiki.multimedia.cx/index.php/JV";
	ext          = [".jv"];
	magic        = ["Bitmap Brothers JV video"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
