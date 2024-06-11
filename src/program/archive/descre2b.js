import {Program} from "../../Program.js";

export class descre2b extends Program
{
	website   = "http://www.retroarchive.org/garbo/pc/arcers/dese2b10.zip";
	loc       = "dos";
	bin       = "DESCRE2B.EXE";
	args      = async r => [r.inFile({backslash : true}), await r.outFile("OUTFILE", {backslash : true})];
	renameOut = true;
}
