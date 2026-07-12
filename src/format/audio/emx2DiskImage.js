import {Format} from "../../Format.js";

export class emx2DiskImage extends Format
{
	name       = "EMAX-II Disk Image";
	magic      = ["E-mu Emaxsynth sample"];
	converters = ["vibe2wav"];
}
