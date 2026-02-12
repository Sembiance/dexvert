import {Format} from "../../Format.js";

export class mid extends Format
{
	name         = "MIDI Music File";
	website      = "http://fileformats.archiveteam.org/wiki/MIDI";
	ext          = [".mid"];
	magic        = [
		// general
		"MIDI Music", "MIDI Audio", "Standard MIDI data", "Karaoke MIDI", "MIDI sequence data", "audio/midi", /^geViewer: MIDI_MTHD( |$)/, /^x-fmt\/230( |$)/,

		// app specific
		"Yamaha General Style"
	];
	idMeta       = ({macFileType, macFileCreator, proDOSTypeCode}) => ["Midi", "MIDI", "MID "].includes(macFileType) || proDOSTypeCode==="MDI" || (["SwTy", "SwTx"].includes(macFileType) && macFileCreator==="MRCL");
	notes        = "Default instrument library used is 'eaw'. Others available: fluid, roland, creative, freepats, windows";
	metaProvider = ["musicInfo"];
	converters   = ["timidity", "gamemus[format:mid-type0]"];
}
