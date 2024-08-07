import {xu} from "xu";
import {Program, RUNTIME} from "../../Program.js";

export class dexvertExternal extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	flags   = {
		asFormat   : "Which format to convert as",
		skipVerify : "Don't verify output file"
	};
	unsafe = true;

	bin  = "/mnt/compendium/bin/dexvert";
	args = r =>
	{
		const a = [`--logLevel=${r.xlog.level}`, `--programFlag=osPriority:true`];
		if(r.flags.asFormat)
			a.push(`--asFormat=${r.flags.asFormat}`);
		if(r.flags.skipVerify)
			a.push("--skipVerify");

		const forbidProgram = new Set(RUNTIME.forbidProgram);
		for(let parentRunState=r.chainParent;parentRunState;parentRunState=parentRunState.chainParent)
			forbidProgram.add(parentRunState.programid);
			
		a.push(...Array.from(forbidProgram, v => `--forbidProgram=${v}`));

		return [...a, "--", r.inFile(), r.outDir()];
	};
	runOptions = r => ({liveOutput : r.xlog.atLeast("trace"), timeout : xu.MINUTE*10});
	renameIn   = false;	// RunState.originalInput would be lost and dexvert should be able to handle any incoming filename
	renameOut  = false;
}
