import {Program} from "../../Program.js";

export class rol2midi extends Program
{
	website   = "https://vgmpf.com/Wiki/index.php?title=ROL_to_MIDI";
	loc       = "dos";
	bin       = "ROL2MIDI/ROL2MIDI.EXE";
	unsafe    = true;
	args      = r => [`..\\..\\${r.inFile()}`, "/BSTANDARD.BNK", `/O..\\..\\${r.f.outDir.base}\\DEXVERT.MID`];
	dosData   = () => ({runIn : "prog"});
	renameOut = true;
	chain     = "timidity";
}
