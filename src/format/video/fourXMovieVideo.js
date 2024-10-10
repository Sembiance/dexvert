import {Format} from "../../Format.js";

export class fourXMovieVideo extends Format
{
	name         = "4X Movie Video";
	website      = "https://wiki.multimedia.cx/index.php/4xm_Format";
	ext          = [".4xm"];
	magic        = ["4X Movie video", "RIFF Datei: unbekannter Typ '4XMV'", "4X Technologies (4xm)", /^RIFF.* 4X Movie/, /^fmt\/1150( |$)/];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg"];
}
