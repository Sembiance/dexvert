import {Format} from "../../Format.js";

export class aPACKPacked extends Format
{
	name       = "aPACK Packed";
	magic      = ["Packer: aPACK", "16bit DOS EXE aPACK compressed"];
	packed     = true;
	converters = ["cup386"];
}
