import {Format} from "../../Format.js";

export class regripsEncryptedAudio extends Format
{
	name           = "Regrips Encrypted Audio Archive";
	ext            = [".dat", ".wav"];	// sometimes multiple samples (audio_resource.dat) and sometimes just a single sample (*.wav)
	forbidExtMatch = true;
	magic          = ["archive:Regrips.AudioResourceOpener"];
	converters     = ["GARbro[types:archive:Regrips.AudioResourceOpener]"];
}
