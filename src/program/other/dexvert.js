import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";
import {DexFile} from "../../DexFile.js";

export class dexvert extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags   = {
		asFormat      : "Which format to convert as",
		forbidProgram : "Specify a program to forbid being ran. Parent programs (if this is chained to) are automatically forbidden",
		skipVerify    : "Don't verify output file"
	};
	unsafe = true;
	loc    = "local";
	exec   = async r =>
	{
		const {dexvert : dexvertFunc} = await import(path.join("..", "..", "dexvert.js"));
		
		const dexOpts = {xlog : r.xlog, programFlag : {osPriority : true}};
		if(r.flags.asFormat)
			dexOpts.asFormat = r.flags.asFormat;
		if(r.flags.skipVerify)
			dexOpts.skipVerify = true;
		if(Object.keys(RUNTIME.globalFlags?.osHint || {}).length)
			dexOpts.programFlag.osHint = {...RUNTIME.globalFlags.osHint};

		const forbidProgram = new Set(RUNTIME.forbidProgram);
		for(let parentRunState=r.chainParent;parentRunState;parentRunState=parentRunState.chainParent)
			forbidProgram.add(parentRunState.programid);
		dexOpts.forbidProgram = Array.from(forbidProgram);
		if(r.flags.forbidProgram)
			dexOpts.forbidProgram.push(r.flags.forbidProgram);

		const outDirPath = r.outDir({absolute : true});
		const tmpOutDirPath = await fileUtil.genTempPath(undefined, "_program_other_dexvert");
		await Deno.mkdir(tmpOutDirPath);
		await dexvertFunc(await DexFile.create(r.inFile({absolute : true})), await DexFile.create(tmpOutDirPath), dexOpts);
		await (await fileUtil.tree(tmpOutDirPath, {depth : 1})).parallelMap(async createdFilePath => await fileUtil.move(createdFilePath, path.join(outDirPath, path.basename(createdFilePath))));
		await fileUtil.unlink(tmpOutDirPath, {recursive : true});
	};
	renameIn  = false;	// RunState.originalInput would be lost and dexvert should be able to handle any incoming filename
	renameOut = false;
}
