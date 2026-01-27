import {Program} from "../../Program.js";

export class quickbms extends Program
{
	website = "https://aluigi.altervista.org/quickbms.htm";
	package = "games-util/quickbms";
	unsafe  = true;
	flags   = {
		bms : "BMS script name without .bms extension (located in bin/bms/)"
	};
	bin       = "quickbms";
	args      = r => [Program.binPath(`bms/${r.flags.bms}.bms`), r.inFile(), r.outDir()];
	renameOut = false;
}
