import {Format} from "../../Format.js";

export class multiArtist extends Format
{
	name       = "multiArtist";
	website    = "http://fileformats.archiveteam.org/wiki/MultiArtist";
	ext        = [".mg1", ".mg2", ".mg4", ".mg8"];
	magic      = ["MultiArtist bitmap", "multiArtist", /^fmt\/1468( |$)/];
	fileSize   = {".mg1" : 19456, ".mg2" : 18688, ".mg4" : [15616, 18688], ".mg8" : 14080};
	converters = ["recoil2png[format:MG2,MG8,MG1,MG4]"];
}
