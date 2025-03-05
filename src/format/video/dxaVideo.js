import {Format} from "../../Format.js";

export class dxaVideo extends Format
{
	name         = "DXA Video";
	website      = "https://wiki.multimedia.cx/index.php?title=DXA";
	ext          = [".dxa"];
	magic        = ["DXA video", "DXA (dxa)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:dxa]"];
}
