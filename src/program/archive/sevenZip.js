import {Program, RUNTIME} from "../../Program.js";
import {path} from "std";
import {fileUtil} from "xutil";

export class sevenZip extends Program
{
	website = "http://p7zip.sourceforge.net/";
	package = "app-arch/p7zip";
	flags   = {
		"rsrcOnly"   : "Only care about the files contained within the output .rsrc folder for things like DLL/EXE extraction",
		"singleFile" : "Likely just a single output result, so rename it to the name of the original input file",
		"type"       : "What archive type to process as (run 7z i  for list"
	};
	bin  = "7z";
	args = r =>
	{
		const a = ["x", "-y", "-ppassword"];

		if(r.flags.type)
			a.push(`-t${r.flags.type}`);

		a.push(`-o${r.outDir()}`, r.inFile());

		return a;
	};

	runOptions = () =>
	{
		if(RUNTIME.globalFlags?.osHint?.macintoshjp || RUNTIME.globalFlags?.osHint?.fmtownsjpy)
			return {env : {LANG : "ja_JP"}};
		
		return {};
	};
	filenameEncoding = () => (RUNTIME.globalFlags?.osHint?.macintoshjp || RUNTIME.globalFlags?.osHint?.fmtownsjpy ? "cp932" : "windows-1252");

	postExec = async r =>
	{
		const topLevelDirs = await fileUtil.tree(r.outDir({absolute : true}), {depth : 1});
		if(topLevelDirs.length!==1 && !r.flags.rsrcOnly)
			return;

		for(const singleDirName of [".rsrc", "$0"])
		{
			const singleDirPath = path.join(r.outDir({absolute : true}), singleDirName);
			if(await fileUtil.exists(singleDirPath) && (await Deno.lstat(singleDirPath)).isDirectory)
				await fileUtil.moveAll(singleDirPath, r.outDir({absolute : true}), {unlinkSrc : true});
		}
	};

	post = r =>
	{
		if(r.stderr.includes("Wrong password"))
			r.meta.passwordProtected = true;
	};

	checkForDups = true;
	verify = (r, dexFile) =>
	{
		// we only filter out files if we are in rsrcOnly mode
		if(!r.flags.rsrcOnly)
			return true;

		const dexFileRel = path.relative(r.outDir({absolute : true}), dexFile.absolute);

		// p7zip extracts things like DIALOGs and other files that are not in a format I can really do anything with, so let's just get rid of them
		// List of resources: https://github.com/jinfeihan57/p7zip/blob/295dac87f657de12f6165cb9d81404e079651a50/CPP/7zip/Archive/PeHandler.cpp#L493
		// GROUP_CURSOR and GROUP_ICON could be 'massaged' into a workable .CUR/.ICO, but I couldn't determine this path and neither p7zip nor wrestool support it: http://manpages.ubuntu.com/manpages/bionic/man1/wrestool.1.html
		// VERSION is usually parsed by p7zip into version.txt, but some resources don't parse correclty (executable/exe/Keypad.exe)
		// MENU could parsed out into a txt file representing the menu, but I'd have to find the binary format spec for these resources, for now, just ditch em
		const SKIP_DIRS = ["ACCELERATOR", "DIALOG", "GROUP_CURSOR", "GROUP_ICON", "MENU", "VERSION"];
		const SKIP_FILENAMES = ["ENGINE", "CODE", "DATA"];
		if(SKIP_DIRS.some(v => dexFileRel.split("/").slice(0, -1).some(dirname => dirname.startsWith(v))) || SKIP_FILENAMES.includes(dexFileRel) || (!dexFileRel.includes("/") && dexFileRel.startsWith(".")))
			return false;

		return true;
	};
	renameOut = r => (r.flags.singleFile ? {} : false);

	chain = "?stripGarbage[null] -> ?fix7zCUR";
	chainCheck = (r, chainFile, programid) =>
	{
		// the output txt files have 0x00 bytes intspaced every other byte, no idea why
		if(programid==="stripGarbage" && (["version.txt", "string.txt"].includes(chainFile.base) || path.basename(chainFile.dir)==="STRING"))
			return true;
		
		if(programid==="fix7zCUR" && path.basename(chainFile.dir)==="CURSOR")
			return {outputFilePath : `${chainFile.absolute}.cur`};

		return false;
	};
}
