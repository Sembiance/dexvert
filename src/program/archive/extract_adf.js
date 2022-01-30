import {xu} from "xu";
import {Program} from "../../Program.js";

export class extract_adf extends Program
{
	website          = "https://github.com/mist64/extract-adf";
	package          = "app-arch/extract-adf";
	bin              = "extract-adf";
	filenameEncoding = "iso-8859-1";						// AmigaOS uses this: http://lclevy.free.fr/adflib/adf_info.html#p54
	args             = r => ["-a", r.inFile()];
	cwd              = r => r.outDir();
	// Some archives when extracted produce huge 600+GB files (3_ODETORAMON3.adf) and this will take care of removing those
	verify           = (r, dexFile) => dexFile.size<(xu.MB*50);
	renameOut        = false;
}
