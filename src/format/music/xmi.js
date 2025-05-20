import {Format} from "../../Format.js";

export class xmi extends Format
{
	name       = "Extended MIDI";
	website    = "http://fileformats.archiveteam.org/wiki/XMI_(Extended_MIDI)";
	ext        = [".xmi"];
	safeExt    = ".xmi";
	magic      = ["Extended MIDI", "XMI (Alt)"];
	converters = dexState => (dexState.hasMagics("XMI (Alt)") ? ["dd[bs:16][skip:1][outExt:.xmi] -> midistar2mp3"] : ["midistar2mp3"]);
}
