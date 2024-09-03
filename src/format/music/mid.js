import {Format} from "../../Format.js";

export class mid extends Format
{
	name         = "MIDI Music File";
	website      = "http://fileformats.archiveteam.org/wiki/MIDI";
	ext          = [".mid"];
	magic        = [
		// general
		"MIDI Music", "MIDI Audio", "Standard MIDI data", "Karaoke MIDI", "MIDI sequence data", /^x-fmt\/230( |$)/,

		// app specific
		"Yamaha General Style"
	];
	idMeta       = ({macFileType}) => macFileType==="Midi";
	notes        = "Default instrument library used is 'eaw'. Others available: fluid, roland, creative, freepats, windows";
	metaProvider = ["musicInfo"];
	converters   = ["timidity", "gamemus[format:mid-type0]"];
}
