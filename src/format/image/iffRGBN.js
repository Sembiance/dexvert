import {Format} from "../../Format.js";

export class iffRGBN extends Format
{
	name       = "IFF RGBN Image";
	website    = "http://fileformats.archiveteam.org/wiki/ILBM";
	ext        = [".iff", ".rgbn"];
	magic      = [/^IFF data, RGB.* image$/, /^IFF .* RGB bitmap$/];
	converters = ["iio2png", "recoil2png"];
}
