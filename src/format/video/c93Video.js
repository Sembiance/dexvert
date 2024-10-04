import {Format} from "../../Format.js";

export class c93Video extends Format
{
	name         = "Interplay C93 Video";
	website      = "https://wiki.multimedia.cx/index.php/C93";
	ext          = [".c93"];
	magic        = ["Interplay C93 (c93)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:c93]"];
}
