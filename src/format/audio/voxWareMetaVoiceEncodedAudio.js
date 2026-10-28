import {Format} from "../../Format.js";

export class voxWareMetaVoiceEncodedAudio extends Format
{
	name           = "VoxWare MetaVoice encoded audio";
	ext            = [".vox"];
	forbidExtMatch = true;
	magic          = ["VoxWare MetaVoice encoded audio"];
	converters     = ["vibe2wav[renameOut]"];
}
