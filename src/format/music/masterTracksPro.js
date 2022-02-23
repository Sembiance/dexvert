import {Format} from "../../Format.js";

export class masterTracksPro extends Format
{
	name        = "Master Tracks Pro";
	ext         = [".mts"];
	magic       = ["Master Tracks Score"];
	unsupported = true;
	notes       = "So the Pro version of Master Tracks Pro software, which I own, can convert this to MIDI, but it only runs on Vista/7/8/10. I could add a QEMU server for Win 7 I suppose, but not really worth it for 1 format.";
}
