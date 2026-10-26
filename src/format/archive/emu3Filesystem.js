import {Format} from "../../Format.js";

export class emu3Filesystem extends Format
{
	name        = "E-Mu III Filesystem";
	magic       = ["E-mu Emulator III sample"];
	unsupported = true;
	// vibe coded extractor avaialble in vibe/legacy/emu3Filesystem/ but haven't found any actual real sample files to test against
}
