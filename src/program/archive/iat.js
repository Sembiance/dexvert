import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class iat extends Program
{
	website    = "https://www.berlios.de/software/iso9660-analyzer-tool/";
	package    = "app-cdr/iat";
	bin        = "iat";
	unsafe     = true;
	args       = r => ["-i", r.inFile(), "--cue", "-o", "out"];
	cwd        = r => r.outDir();
	runOptions = ({timeout : xu.MINUTE*10});	// can hang on things

	postExec = async r =>
	{
		const fileOutputPaths = await fileUtil.tree(r.outDir({absolute : true}));
		// sometimes iat just produces a single .cue file and no corresponding .bin file, so we delete the .cue file so we can try other converters
		if(fileOutputPaths.length===1 && fileOutputPaths[0].endsWith(".cue"))
			await fileUtil.unlink(fileOutputPaths[0]);
	};

	renameOut  = false;
	chain      = "?dexvert[skipVerify][bulkCopyOut]";
	chainCheck = (r, chainFile) => [".bin"].includes(chainFile.ext.toLowerCase());
	chainPost  = async r => await fileUtil.unlink(path.join(r.outDir({absolute : true}), "out.cue"));
}
