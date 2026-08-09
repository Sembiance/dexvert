import {Format} from "../../Format.js";

export class arikaNXMS extends Format
{
	name           = "Arika NXMS Audio";
	ext            = [".nxms"];
	forbidExtMatch = true;
	magic          = ["Arika NXMS (nxms)"];
	metaProvider   = ["ffprobe[libre]"];
	converters     = ["ffmpeg[libre][format:nxms][outType:mp3]"];
}
