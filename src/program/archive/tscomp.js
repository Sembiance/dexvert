import {Program} from "../../Program.js";

export class tscomp extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/TSComp";
	loc     = "dos";
	bin     = "TSCOMP.EXE";
	dosData = async r =>
	{
		const tscompFilenames = (await Program.runProgram("tscompInfo", r.f.input, {xlog : r.xlog, autoUnlink : true})).meta?.tscompFilenames;
		return ({autoExec : tscompFilenames.map(fn => `..\\DOS\\TSCOMP.EXE -d ${r.inFile({backslash : true})} ..\\OUT\\${fn}`)});
	};
	renameOut = false;
}
