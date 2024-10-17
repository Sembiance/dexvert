import {xu} from "xu";
import {Program} from "../../Program.js";

export class uhbc extends Program
{
	website   = "https://www.sac.sk/download/pack/uhbc10.zip";
	loc       = "dos";
	bin       = "UHBC/UHBC.EXE";
	args      = async r => ["d", r.inFile({backslash : true}), await r.outFile("outfile", {backslash : true})];
	renameOut = true;
}
