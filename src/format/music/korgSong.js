import {Format} from "../../Format.js";

export class korgSong extends Format
{
	name        = "Korg Song";
	ext         = [".sng"];
	magic       = ["Korg Song file"];
	unsupported = true;	// 190 unique files on discmaster, but they are essentially MIDI type files but against a KORG sound font/synthesizer, so meh. vibe coder was started in legacy/vibe/korgSong/
}
