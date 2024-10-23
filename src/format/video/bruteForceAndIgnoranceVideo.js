import {Format} from "../../Format.js";

export class bruteForceAndIgnoranceVideo extends Format
{
	name           = "Brute Force and Ignorance video";
	website        = "https://wiki.multimedia.cx/index.php/BFI";
	ext            = [".bfi"];
	forbidExtMatch = true;
	magic          = ["Brute Force and Ignorance video", "Brute Force & Ignorance (bfi)"];
	metaProvider   = ["mplayer"];
	converters     = ["ffmpeg[format:bfi]"];
}
