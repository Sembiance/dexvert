import {Format} from "../../Format.js";

export class eaMADVideo extends Format
{
	name        = "EA MAD Video";
	website     = "https://wiki.multimedia.cx/index.php/Electronic_Arts_MAD";
	magic       = ["Electronic Arts MAD video"];
	unsupported = true;	// only 145 unique files on discmaster, but many are "empty" because they were truncated to fit on various warez discs
}
