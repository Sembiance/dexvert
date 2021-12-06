import {Format} from "../../Format.js";

export class sid extends Format
{
	name         = "Commodore SID Music File";
	website      = "http://fileformats.archiveteam.org/wiki/SID";
	ext          = [".sid", ".psid", ".mus"];
	magic        = ["Play SID Audio", "PlaySID", "SID tune"];
	keepFilename = true;	// Needed to determine proper song length
	metaProvider = ["sidInfo"];
	converters   = dexState => ([[].pushSequence(1, (dexState.meta.sidSubSongCount || 1)).map(i => `sidplay2[subSong:${i}][songLength:${(dexState.meta.sidSongLengths || [])[i-1] || "3:0"}]`).join(" & ")]);
}
