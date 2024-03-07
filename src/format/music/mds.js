import {Format} from "../../Format.js";

export class mds extends Format
{
	name       = "RIFF MIDS File";
	website    = "http://fileformats.archiveteam.org/wiki/RIFF_MIDS";
	ext        = [".mds"];
	magic      = ["RIFF MIDS file", "RIFF Datei: unbekannter Typ 'MIDS'"];
	converters = ["midistar2mp3"];
}
