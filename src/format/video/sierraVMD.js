import {Format} from "../../Format.js";

export class sierraVMD extends Format
{
	name         = "Sierra Video and Music Data";
	website      = "https://wiki.multimedia.cx/index.php/VMD";
	ext          = [".vmd"];
	magic        = ["Sierra Video and Music Data video", "Sierra VMD (vmd)"];
	metaProvider = ["ffprobe"];
	converters   = ["ffmpeg[format:vmd]", "nihav"];
}
