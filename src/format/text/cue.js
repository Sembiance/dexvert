import {xu} from "xu";
import {Format} from "../../Format.js";

export class cue extends Format
{
	name         = "ISO CUE Sheet";
	website      = "http://fileformats.archiveteam.org/wiki/CUE_and_BIN";
	ext          = [".cue"];
	metaProvider = ["text", "cueInfo=>cue"];
	magic        = ["ISO CDImage cue", "Cue Sheet", /^fmt\/1069( |$)/];
	untouched    = dexState => !!dexState.meta.cue;
}
