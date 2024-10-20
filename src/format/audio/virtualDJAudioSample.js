import {Format} from "../../Format.js";

export class virtualDJAudioSample extends Format
{
	name           = "VirtualDJ audio Sample";
	ext            = [".vdj"];
	forbidExtMatch = true;
	magic          = ["VirtualDJ audio Sample"];
	converters     = ["vgmstream"];
}
