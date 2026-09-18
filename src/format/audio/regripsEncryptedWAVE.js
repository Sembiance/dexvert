import {Format} from "../../Format.js";

export class regripsEncryptedWAVE extends Format
{
	name           = "Regrips Encrypted WAVE Audio";
	ext            = [".wav"];
	forbidExtMatch = true;
	magic          = ["audio:Regrips.WrgAudio"];
	converters     = ["GARbro[types:audio:Regrips.WrgAudio]"];
}
