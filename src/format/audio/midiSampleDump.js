import {Format} from "../../Format.js";

export class midiSampleDump extends Format
{
	name         = "MIDI Sample Dump";
	ext          = [".sds"];
	magic        = ["MIDI Sample Dump"];
	metaProvider = ["soxi"];
	converters   = ["sox", "awaveStudio"];
}
