import {Format} from "../../Format.js";

export class musicXSequence extends Format
{
	name        = "Music-X Sequence";
	website     = "http://www.retrocastaway.com/retro-computing/music-x-making-music-on-the-amiga-in-the-80s/";
	ext         = [".seq"];
	magic       = ["Music-X Sequence"];
	unsupported = true;	// not convinced this is music, I think it might just be some meta info
}
