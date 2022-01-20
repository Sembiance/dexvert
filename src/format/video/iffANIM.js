import {Format} from "../../Format.js";

export class iffANIM extends Format
{
	name         = "Interchange File Format Animation";
	website      = "http://fileformats.archiveteam.org/wiki/ANIM";
	ext          = [".anim", ".anm", ".sndanim"];
	magic        = ["IFF data,  ANIM animation", "IFF ANIM"];
	metaProvider = ["mplayer"];
	converters   = ["ffmpeg[format:iff]", "xanim[fps:12]"];
}
