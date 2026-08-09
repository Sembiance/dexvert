import {Format} from "../../Format.js";

export class inevitableAUDIOPKG extends Format
{
	name           = "Inevitable AUDIOPKG";
	ext            = [".audiopkg"];
	forbidExtMatch = true;
	magic          = ["Inevitable AUDIOPKG (audiopkg)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:audiopkg][outType:mp3]"];
}
