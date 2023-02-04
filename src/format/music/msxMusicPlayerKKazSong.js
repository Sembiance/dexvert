import {Format} from "../../Format.js";

export class msxMusicPlayerKKazSong extends Format
{
	name       = "MSX Music Player K-kaz Song";
	ext        = [".mpk"];
	magic      = ["MSX Music Player K-kaz song"];
	converters = ["kss2wav"];
}
