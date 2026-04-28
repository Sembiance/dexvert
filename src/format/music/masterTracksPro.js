import {Format} from "../../Format.js";

export class masterTracksPro extends Format
{
	name        = "Master Tracks Pro";
	ext         = [".mts"];
	magic       = ["Master Tracks Score", "Master Tracks Pro Score"];
	unsupported = true;	// 404 unique files on discmaster, but the format is likely quite complex so unlikely to be successful with a vibe coded converter
	notes       = "Attempts to run Master Tracks Pro under win2k/winxp/win7 64bit, all failed. Program just doesn't launch.";
}
