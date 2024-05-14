import {Format} from "../../Format.js";

export class mid extends Format
{
	name         = "MIDI Music File";
	website      = "http://fileformats.archiveteam.org/wiki/MIDI";
	ext          = [".mid"];
	magic        = ["MIDI Music", "MIDI Audio", "Standard MIDI data", "Karaoke MIDI", /^x-fmt\/230( |$)/];
	idMeta       = ({macFileType}) => macFileType==="Midi";
	notes        = "Default instrument library used is 'eaw'. Others available: fluid, roland, creative, freepats, windows";
	metaProvider = ["musicInfo"];
	converters   = ["timidity", "gamemus[format:mid-type0]"];
}
