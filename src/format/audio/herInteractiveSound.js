import {Format} from "../../Format.js";

export class herInteractiveSound extends Format
{
	name           = "Her Interactive Sound";
	ext            = [".his"];
	forbidExtMatch = true;
	magic          = ["Her Interactive Sound (his)", "Her Interactive Sound 0 (his0)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:his][outType:mp3]", "ffmpeg[libre][format:his0][outType:mp3]"];
}
