import {Format} from "../../Format.js";

export class spectrum512X extends Format
{
	name       = "Spectrum 512 Extended";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_Extended";
	ext        = [".spx"];
	magic      = ["Spectrum 512 Extended bitmap", /^fmt\/(1577|1578)( |$)/];
	converters = ["recoil2png"];
}
