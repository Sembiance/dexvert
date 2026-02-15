import {Format} from "../../Format.js";

export class artStudio extends Format
{
	name       = "Art Studio";
	website    = "http://fileformats.archiveteam.org/wiki/Art_Studio";
	ext        = [".art", ".aas"];
	magic      = ["C64 Hires bitmap", "Art Studio :ocp:"];
	weakMagic  = true;
	fileSize   = [...[].pushSequence(9000, 9010), 10018];
	converters = ["recoil2png[format:ART.Iph,AAS]", "nconvert[format:ocp]", "view64[strongMatch]"];
}
