import {Format} from "../../Format.js";

export class xboxXMV extends Format
{
	name         = "XBOX XMV Video";
	website      = "https://wiki.multimedia.cx/index.php/XMV";
	ext          = [".xmv"];
	magic        = ["Xbox Video", "Microsoft XMV (xmv)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:xmv]"];
}
