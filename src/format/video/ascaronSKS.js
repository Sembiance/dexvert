import {Format} from "../../Format.js";

export class ascaronSKS extends Format
{
	name           = "ASCARON SKS video";
	website        = "https://wiki.multimedia.cx/index.php/Ascorn_SKS";
	ext            = [".sks"];
	forbidExtMatch = true;
	magic          = ["ASCARON video"];
	weakMagic      = true;
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg[format:mjpeg]"];
}
