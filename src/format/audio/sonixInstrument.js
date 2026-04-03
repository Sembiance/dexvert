import {xu} from "xu";
import {Format} from "../../Format.js";

export class sonixInstrument extends Format
{
	name         = "Aegis Sonix Instrument";
	ext          = [".instr", ".ss"];
	magic        = ["Sonix sampled sound Instrument", "Sonix synthesised Instrument"];
	weakMagic    = true;
	keepFilename = true;

	// Both .instr and .ss are required
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));

	// Don't do anything with .ss files
	untouched = ({f}) => f.input.ext.toLowerCase()===".ss";
	verifyUntouched = false;
	converters = ["vibe2wav"];
}
