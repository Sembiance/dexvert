import {Format} from "../../Format.js";

export class xmi extends Format
{
	name       = "Extended MIDI";
	website    = "http://fileformats.archiveteam.org/wiki/XMI_(Extended_MIDI)";
	ext        = [".xmi"];
	magic      = ["Extended MIDI"];
	converters = ["midistar2mp3"];
}
