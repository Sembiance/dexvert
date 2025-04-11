import {Format} from "../../Format.js";

export class enhancedCompressedWavelet extends Format
{
	name           = "Enhanced Compressed Wavelet";
	website        = "http://fileformats.archiveteam.org/wiki/ECW";
	ext            = [".ecw"];
	forbidExtMatch = true;
	magic          = ["Enhanced Compressed Wavelet", /^fmt\/371( |$)/];
	converters     = ["mrsiddecode"];
}
