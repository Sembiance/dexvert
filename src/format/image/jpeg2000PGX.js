import {Format} from "../../Format.js";

export class jpeg2000PGX extends Format
{
	name           = "JPEG 2000 PGX";
	website        = "http://fileformats.archiveteam.org/wiki/PGX_(JPEG_2000)";
	ext            = [".pgx"];
	forbidExtMatch = true;	// pretty rare format and thus don't want too many false matches via ext
	magic          = ["PGX JPEG 2000 bitmap", "piped pgx sequence (pgx_pipe)"];
	metaProvider   = ["image"];
	converters     = ["convert", "ffmpeg[format:pgx_pipe][outType:png]", "wuimg[matchType:magic]"];
}
