import {Format} from "../../Format.js";

export class sonixSoundSample extends Format
{
	name        = "Sonix Sound Sample";
	ext         = [".ss"];
	unsupported = true;
	notes       = "These files are used as the instruments in .smus files. In theory I should be able to convert these instruments into .wav's";
}
