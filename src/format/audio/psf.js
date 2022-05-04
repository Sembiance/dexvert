import {Format} from "../../Format.js";

export class psf extends Format
{
	name         = "Playstation Sound Format";
	website      = "http://fileformats.archiveteam.org/wiki/PSF";
	ext          = [".psf", ".minipsf"];
	magic        = [/^PSF1? Playstation Sound Format rip$/, "Portable Sound Format", /^fmt\/959( |$)/];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}
