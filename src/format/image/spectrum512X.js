import {Format} from "../../Format.js";

export class spectrum512X extends Format
{
	name       = "Spectrum 512 Extended";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats";
	ext        = [".spx"];
	magic      = ["Spectrum 512 Extended bitmap"];
	converters = ["recoil2png"];
}
