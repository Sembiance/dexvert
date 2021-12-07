import {xu} from "xu";
import {Program} from "../../Program.js";

export class gameextractor extends Program
{
	website = "http://www.watto.org/game_extractor.html";
	package = "games-util/gameextractor";
	bin     = "gameextractor";

	// gameextractor requires full absolute paths
	args = r => ["-extract", "-input", r.inFile({absolute : true}), "-output", r.outDir({absolute : true})];

	// gameextractor always opens an X window (thus virtualX) and on some files it just hangs forever (thus timeout)
	runOptions = ({virtualX : true, timeout : xu.MINUTE*1});
	renameOut  = false;

	// Sometimes gameextractor files with _ge_decompressed suffixes in the INPUT dir. Since this is in the INPUT dir, I don't really care
}
