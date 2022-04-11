import {Format} from "../../Format.js";

export class soundTracker extends Format
{
	name         = "SoundTracker Module";
	ext          = [".mod"];
	matchPreExt  = true;
	//priority     = this.PRIORITY.LOW;
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "uade123", "zxtune123", "openmpt123"];
}
