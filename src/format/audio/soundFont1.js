import {Format} from "../../Format.js";

export class soundFont1 extends Format
{
	name           = "SoundFont 1.0";
	website        = "http://fileformats.archiveteam.org/wiki/SoundFont_1.0";
	ext            = [".sbk"];
	forbidExtMatch = true;
	magic          = ["SoundFont 1.0", "Emu Sound Font (v1.0)"];
	converters     = ["awaveStudio"];
}
