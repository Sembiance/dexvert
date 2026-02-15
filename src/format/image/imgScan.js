import {Format} from "../../Format.js";

export class imgScan extends Format
{
	name             = "IMG Scan";
	website          = "http://fileformats.archiveteam.org/wiki/IMG_Scan";
	ext              = [".rwl", ".raw", ".rwh"];
	fileSize         = {".rwl" : 64000, ".raw" : 128_000, ".rwh" : 256_000};
	matchFileSize    = true;
	confidenceAdjust = () => -19;	// Very weak format, so set it as nearly last
	converters       = ["recoil2png[format:RWL,RAW.Rw,RWH]", "wuimg[format:imgscan]"];
}
