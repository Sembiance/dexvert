import {Format} from "../../Format.js";

export class scre2bPacked extends Format
{
	name       = "SCRE2B Packed";
	website    = "http://fileformats.archiveteam.org/wiki/SCRE2B";
	magic      = ["Packer: SCRE2B", "16bit DOS SCRE2B Command"];
	packed     = true;
	converters = ["descre2b"];
}
