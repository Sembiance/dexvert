import {Program} from "../../Program.js";

export class unadf extends Program
{
	website          = "http://lclevy.free.fr/adflib/";
	package          = "app-arch/unadf";
	bin              = "unadf";
	args             = r => [r.inFile(), "-d", r.outDir()];
	filenameEncoding = "iso-8859-1";	// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	renameOut        = false;
}
