import {Format} from "../../Format.js";

export class threeGVideo extends Format
{
	name         = "3GP/3GPP2 Video";
	website      = "http://fileformats.archiveteam.org/wiki/3GP";
	ext          = [".3gp", ".3g2"];
	magic        = ["3GPP/3GPP2 multimedia audio/video", "ISO Media, MPEG v4 system, 3GPP2"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
