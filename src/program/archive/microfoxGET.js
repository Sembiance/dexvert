import {Program} from "../../Program.js";

export class microfoxGET extends Program
{
	website   = "https://archive.org/details/msdos_festival_PUT345";
	unsafe    = true;
	loc       = "dos";
	bin       = "GET.EXE";
	args      = r => [r.inFile({backslash : true}), `E:\\${r.f.outDir.base}`, "QUIET"];
	renameOut = false;
}
