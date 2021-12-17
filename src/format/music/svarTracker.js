import {Format} from "../../Format.js";

export class svarTracker extends Format
{
	name        = "SVArTracker Module";
	website     = "https://www.kvraudio.com/product/svartracker-by-svar-software";
	ext         = [".svar"];
	magic       = ["SVArTracker module"];
	notes       = "I tried using sandbox/app/svartracker_1_22_free_inst.exe under win2k but got lots of errors and couldn't even figure out how to 'render' the file to WAV, VERY clumsy program and only a tiny handful of songs seem to exist for it.";
	unsupported = true;
}
