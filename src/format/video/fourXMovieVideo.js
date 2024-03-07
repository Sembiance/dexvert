import {Format} from "../../Format.js";

export class fourXMovieVideo extends Format
{
	name         = "4X Movie Video";
	website      = "https://wiki.multimedia.cx/index.php/4xm_Format";
	ext          = [".4Xm"];
	magic        = ["4X Movie video", "RIFF Datei: unbekannter Typ '4XMV'", /^fmt\/1150( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
