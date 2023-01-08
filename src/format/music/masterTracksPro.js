import {Format} from "../../Format.js";

export class masterTracksPro extends Format
{
	name        = "Master Tracks Pro";
	ext         = [".mts"];
	magic       = ["Master Tracks Score"];
	unsupported = true;
	notes       = "Master Tracks Pro (app in sandbox/app/master_tracks_pro_full.exe and S/N is in email) can convert this to MIDI, but it only runs on Vista/7/8/10.";
}
