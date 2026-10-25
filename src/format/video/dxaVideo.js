import {Format} from "../../Format.js";

export class dxaVideo extends Format
{
	name         = "DXA Video";
	website      = "https://wiki.multimedia.cx/index.php/DXA";
	ext          = [".dxa"];
	magic        = ["DXA video", "DXA (dxa)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:dxa]"];
}
