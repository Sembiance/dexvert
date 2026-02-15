import {Format} from "../../Format.js";

export class multiColor extends Format
{
	name       = "ZX Spectrum Multicolor";
	website    = "http://fileformats.archiveteam.org/wiki/Multicolor_(ZX_Spectrum)";
	ext        = [".ifl", ".mc", ".mlt"];
	fileSize   = {".ifl" : 9216, ".mc,.mlt" : 12288};
	converters = ["recoil2png[format:IFL.ZxIfl,MLT,MC]"];
}
