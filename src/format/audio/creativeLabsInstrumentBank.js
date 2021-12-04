import {Format} from "../../Format.js";

export class creativeLabsInstrumentBank extends Format
{
	name        = "Creative Labs Instrument Bank";
	website     = "http://fileformats.archiveteam.org/wiki/Instrument_Bank";
	ext         = [".ibk"];
	magic       = ["IBK instrument data", "Sound Blaster Instrument Bank"];
	unsupported = true;
}
