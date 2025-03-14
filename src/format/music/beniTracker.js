import {Format} from "../../Format.js";

export class beniTracker extends Format
{
	name           = "Beni Tracker Module";
	website        = "http://fileformats.archiveteam.org/wiki/Beni_Tracker_module";
	ext            = [".pis"];
	forbidExtMatch = true;
	magic          = ["Beni Tracker module"];
	weakMagic      = true;	// just bytes 0x00 01 02 03 04 05 06 at pos 3
	unsupported    = true;
}
