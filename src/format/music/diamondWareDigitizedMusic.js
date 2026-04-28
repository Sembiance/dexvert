import {Format} from "../../Format.js";

export class diamondWareDigitizedMusic extends Format
{
	name           = "DiamondWare Digitized Music";
	website        = "http://fileformats.archiveteam.org/wiki/DiamondWare_Digitized";
	ext            = [".dwm"];
	forbidExtMatch = true;
	magic          = ["DiamondWare Music"];
	unsupported    = true;	// 206 unique files on discmaster, but tricky to vibe code a converter for I think
	notes          = "Some kind of wrapped MIDI modified for OPL commands. Can be played with DOS PLAYDWM.EXE but no known converter back to midi or .wav";
}
