import {xu} from "xu";
import {Format} from "../../Format.js";

export class superscapeSounds extends Format
{
	name  = "Superscape Sounds";
	ext   = [".snd"];
	magic = [/^Superscape Sounds$/];
	notes = xu.trim`
		Not yet supported. This can convert it: sox -t raw -r 11025 -e signed -b 16 -c 2 sounds.snd b.wav
		In the UI you can see the 'pitch' which corresponds to the rate: 64===11025hz and 40===44100hz
		However there are several sounds packed into this file, not just 1 sound, and they may differ in rate/pitch, etc.
		So ideally the format needs to be figured out so each sound can be extracted separately.`;
	unsupported = true;
}
