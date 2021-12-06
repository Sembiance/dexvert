
import {Format} from "../../Format.js";

export class hmi extends Format
{
	name       = "Human Machine Interfaces MIDI Format";
	website    = "http://fileformats.archiveteam.org/wiki/HMI";
	ext        = [".hmi", ".hmp"];
	magic      = ["Human Machine Interfaces MIDI Format"];
	converters = ["midistar2mp3"];
}
