import {Format} from "../../Format.js";

export class vqf extends Format
{
	name       = "VQF TwinVQ";
	website    = "https://wiki.multimedia.cx/index.php/VQF";
	ext        = [".vqf"];
	magic      = ["VQF data", "TwinVQF audio", "Nippon Telegraph and Telephone Corporation (NTT) TwinVQ (vqf)"];
	converters = ["ffmpeg[format:vqf][outType:mp3]"];	// TwinDec from http://www.rarewares.org/rrw/nttvqf.php failed to work
}
