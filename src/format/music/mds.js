import {Format} from "../../Format.js";

export class mds extends Format
{
	name       = "RIFF MIDS MIDI Stream";
	website    = "http://fileformats.archiveteam.org/wiki/RIFF_MIDS";
	ext        = [".mds"];
	magic      = ["RIFF MIDS file", "RIFF Datei: unbekannter Typ 'MIDS'", "Generic RIFF file MIDS", "MIDI Stream", /^RIFF.* MIDI Stream/];
	converters = ["midistar2mp3"];
}
