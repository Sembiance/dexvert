import {Format} from "../../Format.js";

export class zxBorderScreen extends Format
{
	name     = "ZX Spectrum Border Screen";
	website  = "http://fileformats.archiveteam.org/wiki/Border_Screen";
	ext      = [".bmc4", ".bsc"];
	fileSize = {".bsc" : 11136, ".bmc4" : 11904};
	converters = ["recoil2png"];
}
