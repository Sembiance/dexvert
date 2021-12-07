import {Program} from "../../Program.js";

export class extract_adf extends Program
{
	website          = "https://github.com/mist64/extract-adf";
	package          = "app-arch/extract-adf";
	bin              = "extract-adf";
	filenameEncoding = "iso-8859-1";	// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	args             = r => ["-a", r.inFile()];
	cwd              = r => r.outDir();
	renameOut        = false;
}
