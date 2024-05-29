import {Format} from "../../Format.js";

export class soundFont1 extends Format
{
	name        = "SoundFont 1.0";
	website     = "http://fileformats.archiveteam.org/wiki/SoundFont_1.0";
	ext         = [".sbk"];
	magic       = ["SoundFont 1.0", "Emu Sound Font (v1.0)"];
	unsupported = true;
	notes       = "Awave Studio can technically convert these, but 99.9% of all SBK SoundFond 1 files just contain meta info that points to a samples in ROM, thus there isn't anything really to convert.";
}
