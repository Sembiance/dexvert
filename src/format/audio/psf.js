import {Format} from "../../Format.js";

export class psf extends Format
{
	name           = "Portable Sound Format";
	website        = "http://fileformats.archiveteam.org/wiki/Portable_Sound_Format";
	ext            = [".psf", ".minipsf", ".dsf"];
	forbidExtMatch = true;
	magic          = [/^PSF1? Playstation Sound Format rip/, "Portable Sound Format", "Dreamcast Sound Format", "audio/x-psf", /^fmt\/959( |$)/];
	metaProvider   = ["musicInfo"];
	converters     = ["zxtune123"];
}
