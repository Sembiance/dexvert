import {Format} from "../../Format.js";

export class masterTracksPro extends Format
{
	name        = "Master Tracks Pro";
	ext         = [".mts"];
	magic       = ["Master Tracks Score"];
	unsupported = true;
	notes       = "Attempts to run Master Trakcks Pro under win2k/winxp/win7 64bit, all failed. Program just doesn't launch.";
}
