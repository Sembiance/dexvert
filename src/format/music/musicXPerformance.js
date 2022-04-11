import {Format} from "../../Format.js";

export class musicXPerformance extends Format
{
	name        = "Music-X Performance";
	website     = "http://www.retrocastaway.com/retro-computing/music-x-making-music-on-the-amiga-in-the-80s/";
	ext         = [".mx", ".perf"];
	magic       = ["Music-X Performance"];
	unsupported = true;
}
