import {Format} from "../../Format.js";

export class digiTrekker extends Format
{
	name        = "DigiTrekker";
	website     = "http://fileformats.archiveteam.org/wiki/DigiTrekker_module";
	ext         = [".dtm"];
	magic       = ["DigiTrekker DTM Module", "Digitrekker module"];
	unsupported = true;	// ok, 646 unique files on discmaster, BUT they reference external instruments. Sometimes they live in the current song's dir, sometimes somewhere else at player level. Abandoned converter for now, but see vibe/legacy/digiTrekker/
	notes       = "DigiTrekker for MSDOS can play these and convert to a 'SND' format, but only in 'realtime' and I couldn't determine the format of the output SND. milkytracker claims support for this format, but I couldn't get it to play any DTM files.";
}
