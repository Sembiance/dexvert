import {Format} from "../../Format.js";

export class emu3Filesystem extends Format
{
	name        = "E-Mu III Filesystem";
	magic       = ["E-mu Emulator III sample"];
	unsupported = true;
}
