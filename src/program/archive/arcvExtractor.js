import {Program} from "../../Program.js";

export class arcvExtractor extends Program
{
	website   = "https://ia801900.us.archive.org/view_archive.php?archive=/29/items/ctib98_3/ctib98_3.zip";
	loc       = "dos";
	bin       = "ESTPPRO/EXTRACT.EXE";
	args      = r => [`/E:${r.inFile({backslash : true})}`, "/S", "*.*"];
	cwd       = r => r.outDir();
	dosData   = () => ({runIn : "out"});
	renameOut = true;
}
