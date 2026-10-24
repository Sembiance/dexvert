import {Format} from "../../Format.js";

export class inevitableAUDIOPKG extends Format
{
	name           = "Inevitable AUDIOPKG";
	ext            = [".audiopkg"];
	forbidExtMatch = true;
	magic          = ["Inevitable AUDIOPKG (audiopkg)", "vgmstream: audiopkg"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:audiopkg][outType:mp3]", "vgmstream[types:audiopkg]"];
}
