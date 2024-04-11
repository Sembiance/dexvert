import {xu} from "xu";
import {Format} from "../../Format.js";

export class ayAMAD extends Format
{
	name         = "AY Amadeus Chiptune";
	magic        = ["AY Amadeus chiptune"];
	ext          = [".amad"];
	metaProvider = ["ayInfo"];
	converters   = dexState => ([[].pushSequence(0, (dexState.meta.trackCount || 1)-1).map(i => `ayEmul[songCount:${dexState.meta.trackCount}][subSong:${i}][songName:${dexState.meta.titles?.[i]?.replaceAll("]", " ")}]`).join(" & ")]);
}
