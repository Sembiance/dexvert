import {Format} from "../../Format.js";

export class rmi extends Format
{
	name         = "RIFF MIDI Music";
	website      = "http://fileformats.archiveteam.org/wiki/RIFF_MIDI";
	ext          = [".rmi"];
	magic        = ["RMI RIFF MIDI Music", "RIFF-based MIDI", /^RIFF.* data, MIDI$/];
	metaProvider = ["musicInfo"];
	converters   = ["timidity"];
}
