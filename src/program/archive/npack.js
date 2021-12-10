import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class npack extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/NPack";
	unsafe  = true;
	loc     = "dos";
	bin     = "NDFIX-1/NPACK.EXE";
	args    = async r => [r.inFile({backslash : true}), await r.outFile("OUTFILE", {backslash : true})];

	// if the output file begins with the NPack header, then extraction failed
	verify = async (r, dexFile) =>
	{
		const headerBuf = await fileUtil.readFileBytes(dexFile.absolute, 5);
		return headerBuf.indexOfX([0x4D, 0x53, 0x54, 0x53, 0x4D])!==0;
	};

	renameOut     = {
		alwaysRename : true,
		renamer      : [({newName, suffix, originalExt}) => [newName, suffix, originalExt.endsWith("$") ? originalExt.slice(0, -1) : originalExt]]
	};
}
