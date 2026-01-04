import {xu} from "xu";
import {Program} from "../../Program.js";

export class adplay extends Program
{
	website    = "https://github.com/adplug/adplay-unix";
	package    = "media-sound/adplay";

	// Some files like mkJamz/SAMPLE.MKJ will just create massive multi-gigabyte files, it's all valid audio, but no way to instruct it to stop sooner
	diskQuota = xu.MB*500;

	bin        = "adplay";
	args       = async r => ["--once", "-O", "disk", "-d", await r.outFile("out.wav"), r.inFile()];
	runOptions = ({timeout : xu.SECOND*20});	// some files will play and loop forever (music/mkJamz/pcs2 1.mkj)

	// adplay often fails to produce a valid wav but does produce a 44 byte wav file of nothing
	verify    = (r, dexFile) => dexFile.size!==44;
	renameOut = true;

	// we chain to ffmpeg first because due to the diskQuota we sometimes end up with malformed wav files that ffmpeg handles fine but sox doesn't
	chain     = `ffmpeg[outType:wav] -> sox[type:wav][maxDuration:${xu.MINUTE*10}]`;
}
