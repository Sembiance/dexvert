import {Format} from "../../Format.js";

export class psf2 extends Format
{
	name       = "Playstation 2 Sound Format";
	website    = "http://fileformats.archiveteam.org/wiki/PSF2";
	ext        = [".psf2"];
	magic      = ["PSF2 Playstation 2 Sound Format rip"];
	converters = ["zxtune123"];
}
