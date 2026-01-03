import {Format} from "../../Format.js";

export class twoZeroEightAudio extends Format
{
	name           = "208 Audio (Ocean Games)";
	ext            = [".bnk"];
	forbidExtMatch = true;
	magic          = ["208 Audio (Ocean Games)", "208 (Ocean Games) (208)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:208][outType:mp3]"];
}
