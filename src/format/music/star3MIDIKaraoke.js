import {Format} from "../../Format.js";

export class star3MIDIKaraoke extends Format
{
	name           = "Star 3 MIDI Karaoke";
	website        = "https://wiki.multimedia.cx/index.php/Star_3";
	ext            = [".st3"];
	forbidExtMatch = true;
	magic          = ["Star 3 MIDI Karaoke file"];
	converters     = ["vibe2mid"];
}
