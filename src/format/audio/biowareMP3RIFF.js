import {xu} from "xu";
import {Format} from "../../Format.js";

export class biowareMP3RIFF extends Format
{
	name           = "Bioware MP3 RIFF";
	ext            = [".wav"];
	forbidExtMatch = true;
	magic          = ["vgmstream: bw_mp3_riff"];
	converters     = ["vgmstream[types:bw_mp3_riff]"];
}
