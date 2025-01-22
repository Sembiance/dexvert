import {Format} from "../../Format.js";

export class sfpackPacked extends Format
{
	name       = "SFPack Compressed SoundFont";
	ext        = [".sfpack"];
	magic      = ["SFPack compressed SoundFont"];
	converters = ["sfpack"];
}
