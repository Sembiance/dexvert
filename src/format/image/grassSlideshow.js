import {Format} from "../../Format.js";

export class grassSlideshow extends Format
{
	name       = "Grass' Slideshow";
	website    = "http://fileformats.archiveteam.org/wiki/Grass'_Slideshow";
	ext        = [".hpm"];

	// HPM from Atari is always 19203 size, but recoil2png does not support it
	// So if we get to this format, we need to ensure that we don't try converting it because recoil2png will just produce garbage
	idCheck = inputFile => inputFile.size!==19203;

	converters = ["recoil2png[format:HPM]"];
}
