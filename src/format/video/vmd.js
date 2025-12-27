import {Format} from "../../Format.js";

export class vmd extends Format
{
	name         = "Video and Music Data";
	website      = "https://wiki.multimedia.cx/index.php/VMD";
	ext          = [".vmd"];
	magic        = ["Video and Music Data", "VMD (vmd)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:vmd]", "nihav"];
}
