import {Program} from "../../Program.js";

export class softlib extends Program
{
	website = "http://files.shikadi.net/moddingwiki/tools/kdreams/softlib.exe";
	loc     = "dos";
	bin     = "SOFTLIB.EXE";
	cwd     = r => r.outDir();
	dosData = async r =>
	{
		const filenames = (await Program.runProgram(`softlibList[outDirname:${r.f.outDir.base}]`, r.f.input, {xlog : r.xlog, autoUnlink : true})).meta?.softlibFilenames;
		return ({autoExec : filenames.map(fn => `..\\DOS\\SOFTLIB.EXE E ${r.inFile({backslash : true})} ${fn}`), runIn : "out"});
	};
	renameOut = false;
}
