import {Format} from "../../Format.js";

export class pro24SNG extends Format
{
	name        = "Steinberg Pro Song";
	website     = "https://www.atarimania.com/utility-atari-st-pro-24-iii_29596.html";
	ext         = [".sng"];
	magic       = ["Pro 24 MIDI SNG"];
	unsupported = true;
	notes       = "I could emulate Atari ST in Win7, pre-generate a floppy with the song on it, use autoit to send keystrokes to Hatari emulator to load the song and then export as MIDI to the floppy and copy the floppy to c:\\out";
}
