import {Format} from "../../Format.js";

export class rmi extends Format
{
	name         = "RIFF MIDI Music";
	website      = "http://fileformats.archiveteam.org/wiki/RIFF_MIDI";
	ext          = [".rmi"];
	magic        = ["RMI RIFF MIDI Music", "RIFF-based MIDI", "RIFF Datei: unbekannter Typ 'RMID'", /^RIFF.* data, MIDI$/, /^fmt\/956( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["timidity"];
}
