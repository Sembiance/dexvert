import {Format} from "../../Format.js";

export class gfaBASICAtari extends Format
{
	name       = "GFA-BASIC Atari";
	website    = "http://fileformats.archiveteam.org/wiki/Atari_BASIC_tokenized_file";
	ext        = [".gfa", ".bas"];
	weakExt    = [".bas"];
	magic      = ["GFA-BASIC Atari", "GFA-BASIC 3 data"];
	notes      = "The gfalist program only supports decompiling tokenized files of version 3 and higher.";
	converters = ["gfalist"];
}
