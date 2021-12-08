import {xu} from "xu";
import {Program} from "../../Program.js";

export class c1541 extends Program
{
	website = "https://vice-emu.sourceforge.io/";
	package = "app-emulation/vice";
	
	// Some D64 disks such as barbarn2.d64 can cause c1541 to consume all available drive space. See VICE bug #1542: https://sourceforge.net/p/vice-emu/bugs/1542/
	diskQuota = xu.MB*20;
	
	bin        = "c1541";
	args       = () => [];
	cwd        = r => r.outDir();
	runOptions = r => ({timeout : xu.MINUTE, timeoutSignal : "SIGKILL", stdinData : `attach "${r.inFile({absolute : true})}"\nextract\nquit\n`});
	renameOut  = false;
}

// NOTE: Node version used to rename all files, sticking any 1 to 3 digit extension prefix at the end as a suffix instead.
// I have chosen not to do that in this new deno version, as a format can matchPreExt if needed
