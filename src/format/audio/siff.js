import {xu} from "xu";
import {Format} from "../../Format.js";

export class siff extends Format
{
	name    = "Beam Software SIFF Sound";
	website = "http://fileformats.archiveteam.org/wiki/SIFF";
	ext     = [".son"];
	magic   = ["Beam Software SIFF sound", "Beam Software SIFF (siff)", /^fmt\/1559( |$)/];
	notes   = xu.trim`
		The .son test files are technically supported by libavformat and ffmpeg/cvlc, yet it often produces very distored WAVs.
		My hunch is the decompression algo doesn't quite work with my particular test SIFF files. I couldn't locate ANY OTHER converters.`;
	converters = ["na_game_tool[format:siff][outType:wav]", "ffmpeg[format:siff][outType:mp3]"];
}
