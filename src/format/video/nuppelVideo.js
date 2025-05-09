import {Format} from "../../Format.js";

export class nuppelVideo extends Format
{
	name         = "NuppelVideo";
	website      = "https://wiki.multimedia.cx/index.php/Nuppelvideo";
	ext          = [".nuv"];
	magic        = ["NuppelVideo (MythTV) video", "NuppelVideo (nuv)", "NuppelVideo video", /^MythTV NuppelVideo/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:nuv]"];
}
