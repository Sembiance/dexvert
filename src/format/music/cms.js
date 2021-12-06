import {xu} from "xu";
import {Format} from "../../Format.js";

export class cms extends Format
{
	name        = "Creative Music System File";
	website     = "http://fileformats.archiveteam.org/wiki/CMS_(Creative_Music_System)";
	ext         = [".cms"];
	magic       = ["Creative Music System music"];
	unsupported = true;
	notes       = xu.trim`
		Creative Music System. Couldn't locate any information on the file format itself, nor can I find any 'converters' for it.
		Only way to play them is within DOSBOX by setting this in the DOSBOX config:
		[sblaster]
		sbtype  = gb
		sbbase  = 220
		irq     = 7
		dma     = 1
		hdma    = 5
		sbmixer = true
		oplmode = cms
		oplemu  = default
		oplrate = 22050
		Then going into CMSPLAY, running CMSDRV.COM and then PLAYER.EXE
		However that just plays the file, on an infinite loop, in real time. So while in theory I could maybe make a virtual WAV sound driver under linux and
		then have DOSBOX play to that driver and then record the music that way, I'd have to wait for the song to play in real time and there is no info on how long the song is`;
}
