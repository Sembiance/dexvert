import {Format} from "../../Format.js";

export class twinTrackPlayer extends Format
{
	name         = "Twin TrackPlayer";
	ext          = [".dmo"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay"];
}
