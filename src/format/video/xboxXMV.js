import {Format} from "../../Format.js";

export class xboxXMV extends Format
{
	name         = "XBOX XMV Video";
	website      = "https://wiki.multimedia.cx/index.php/XMV";
	ext          = [".xmv"];
	magic        = ["Xbox Video", "Microsoft XMV (xmv)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:xmv]"];
}
