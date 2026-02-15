import {Format} from "../../Format.js";

export class zxCHR extends Format
{
	name       = "ZX Spectrum CHR$";
	website    = "http://fileformats.archiveteam.org/wiki/CH$";
	ext        = [".ch$"];
	magic      = ["ZX Spectrum CHR$ bitmap", "ZX Spectrum CHR"];
	converters = ["recoil2png[format:CH$]"];
}
