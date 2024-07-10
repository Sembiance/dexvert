import {Format} from "../../Format.js";

export class spaceMakerPacked extends Format
{
	name       = "SpaceMaker Packed";
	magic      = ["16bit DOS EXE Spacemaker compressed"];
	packed     = true;
	converters = ["cup386"];
}
