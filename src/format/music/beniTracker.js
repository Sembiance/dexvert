import {Format} from "../../Format.js";

export class beniTracker extends Format
{
	name           = "Beni Tracker Module";
	website        = "http://fileformats.archiveteam.org/wiki/Beni_Tracker_module";
	ext            = [".pis"];
	forbidExtMatch = true;
	magic          = ["Beni Tracker module"];
	weakMagic      = true;
	unsupported    = true;
}
