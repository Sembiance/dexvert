import {xu} from "xu";
import {Program} from "../../Program.js";

export class gameextractorCLI extends Program
{
	website      = "http://www.watto.org/game_extractor.html";
	package      = "games-util/gameextractor";
	bin          = "gameextractor";
	checkForDups = true;

	// NOTE! PREFER using gameextractor server in gameextractor.js over this one. Only use this one if there are like a ton of format codes

	// gameextractor requires full absolute paths
	args = r => ["-extract", "-input", r.inFile({absolute : true}), "-output", r.outDir({absolute : true})];

	// gameextractor always opens an X window (thus virtualX) and on some files it just hangs forever (thus timeout)
	runOptions = ({virtualX : true, timeout : xu.MINUTE*1, killChildren : true});
	verify     = (r, dexFile) => dexFile.size>1 && dexFile.size<Math.max(r.f.input.size*3, xu.MB*5);		// some files are mistakenly identified as zlib and HUGE files are created
	renameOut  = false;

	// Sometimes gameextractor files with _ge_decompressed suffixes in the INPUT dir. Since this is in the INPUT dir, I don't really care
}
