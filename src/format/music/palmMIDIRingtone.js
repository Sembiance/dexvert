import {Format} from "../../Format.js";

export class palmMIDIRingtone extends Format
{
	name           = "Palm Standard Midi File Ringtone";
	ext            = [".pdb"];
	forbidExtMatch = true;
	magic          = ["Palm Standard Midi File Ringtone"];
	converters     = ["unPalmMIDIRingtone"];
}
