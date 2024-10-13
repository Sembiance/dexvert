import {Format} from "../../Format.js";

export class vp6EncodedVideo extends Format
{
	name           = "On2 VP6 encoded video";
	website        = "https://wiki.multimedia.cx/index.php/On2_VP6";
	ext            = [".vp6"];
	magic          = ["VP6 encoded video"];
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg"];
}
