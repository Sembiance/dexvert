import {Format} from "../../Format.js";

export class smjpeg extends Format
{
	name         = "Loki SDL MJPEG Video";
	website      = "https://wiki.multimedia.cx/index.php/SMJPEG";
	ext          = [".mjpg"];
	magic        = ["SMJPEG video", /^SMJPEG .*data, \d+ frames/, "Loki SDL MJPEG (smjpeg)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:smjpeg]"];
}
