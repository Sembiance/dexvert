import {Program} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class sevenZip extends Program
{
	website = "http://p7zip.sourceforge.net/";
	package = "app-arch/p7zip";
	flags   = {
		"rsrcOnly"   : "Only care about the files contained within the output .rsrc folder for things like DLL/EXE extraction",
		"singleFile" : "Likely just a single output result, so rename it to the name of the original input file",
		"type"       : "What archive type to process as"
	};
	bin  = "7z";
	args = r =>
	{
		const a = ["x", "-y"];

		if(r.flags.type)
			a.push(`-t${r.flags.type}`);

		a.push(`-o${r.outDir()}`, r.inFile());

		return a;
	};

	postExec = async r =>
	{
		// we only move files if we are in rsrcOnly mode
		if(!r.flags.rsrcOnly)
			return;

		// the .rsrc directory is kinda useless, so we move anything in it up one dir
		await fileUtil.moveAll(path.join(r.outDir({absolute : true}), ".rsrc"), r.outDir({absolute : true}), {unlinkSrc : true});
	};


	verify = (r, dexFile) =>
	{
		// we only filter out files if we are in rsrcOnly mode
		if(!r.flags.rsrcOnly)
			return true;

		const dexFileRel = path.relative(r.outDir({absolute : true}), dexFile.absolute);

		// 7z extracts things like DIALOGs, but it's not in a format I can really do anything with, so let's just get rid of it
		if(dexFileRel.startsWith("DIALOG/") || ["ENGINE", "CODE", "DATA"].includes(dexFileRel) || (!dexFileRel.includes("/") && dexFileRel.startsWith(".")))
			return false;

		return true;
	};
	renameOut = r => (r.flags.singleFile ? {} : false);

	chain = "?stripGarbage -> ?fix7zCUR";
	chainCheck = (r, chainFile, programid) =>
	{
		if(programid==="stripGarbage" && ["version.txt", "string.txt"].includes(chainFile.base))
			return true;
		
		if(programid==="fix7zCUR" && path.basename(chainFile.dir)==="CURSOR")
			return {outputFilePath : `${chainFile.absolute}.cur`};

		return false;
	};
}
