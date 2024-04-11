import {Format} from "../../Format.js";

export class ay extends Format
{
	name         = "AY Amadeus Chiptune";
	website      = "http://fileformats.archiveteam.org/wiki/AY";
	ext          = [".ay", ".emul"];
	magic        = ["Spectrum 128 tune", "AY chiptune"];
	metaProvider = ["musicInfo", "ayInfo"];
	converters   = dexState => ([[].pushSequence(0, (dexState.meta.trackCount || 1)-1).map(i => `ayEmul[songCount:${dexState.meta.trackCount}][subSong:${i}][songName:${dexState.meta.titles?.[i]?.replaceAll("]", " ")}]`).join(" & "), "zxtune123"]);
}
