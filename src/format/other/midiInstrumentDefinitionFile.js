import {Format} from "../../Format.js";

export class midiInstrumentDefinitionFile extends Format
{
	name           = "MIDI Instrument Definition File";
	website        = "http://fileformats.archiveteam.org/wiki/MIDI_Instrument_Definition_File";
	ext            = [".idf"];
	forbidExtMatch = true;
	magic          = ["MIDI Instrument Definition File", "RIFF Datei: unbekannter Typ 'IDF '"];
	converters     = ["strings"];
}
