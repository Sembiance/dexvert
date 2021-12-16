import {Format} from "../../Format.js";

export class neochromeAnimation extends Format
{
	name       = "NEOchrome Animation";
	website    = "http://fileformats.archiveteam.org/wiki/NEOchrome_Animation";
	ext        = [".ani"];
	magic      = ["Atari NEOchrome animation"];
	converters = ["deark -> *joinAsGIF -> ffmpeg"];
}
