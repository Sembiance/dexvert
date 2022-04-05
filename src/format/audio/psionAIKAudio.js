import {Format} from "../../Format.js";

export class psionAIKAudio extends Format
{
	name        = "Psion AICA Audio";
	ext         = [".aik"];
	magic       = ["Psion serie 3 AICA Sound Compressor audio"];
	unsupported = true;
}
