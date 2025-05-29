import {Format} from "../../Format.js";

export class iffANIM extends Format
{
	name         = "Interchange File Format Animation";
	website      = "http://fileformats.archiveteam.org/wiki/ANIM";
	ext          = [".anim", ".anm", ".sndanim"];
	magic        = ["IFF data, ANIM animation", "IFF ANIM", "AnimBrush", "Deluxe Paint AnimBrush", "deark: anim (IFF-ANIM)"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:iff]", "xanim[matchType:magic][fps:12]", "iff_convert[framesOnly] -> *ffmpeg[fps:15]", "deark[module:anim] -> *ffmpeg[fps:15]"];
}
