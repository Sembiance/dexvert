import {Format} from "../../Format.js";

export class axePacked extends Format
{
	name       = "AXE Packed";
	magic      = ["16bit DOS AXE compressed Executable", "16bit DOS EXE AXE compressed"];
	packed     = true;
	converters = ["unp", "cup386"];
}
