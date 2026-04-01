import {Format} from "../../Format.js";

export class creativeLabsInstrumentBank extends Format
{
	name        = "Creative Labs Instrument Bank";
	website     = "http://fileformats.archiveteam.org/wiki/Instrument_Bank";
	ext         = [".ibk"];
	magic       = ["IBK instrument data", "Sound Blaster Instrument Bank"];
	unsupported = true;	// only 210 uniqe files on discmaster, most are either 60 bytes or 3kb, so likely no actual audio within
	notes       = "gamemus supports reading this format, but doesn't have a way to convert or extract it";
}
