import {xu} from "xu";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";
import {path} from "std";

export class xanim extends Program
{
	website = "https://github.com/Sembiance/xanim";
	package = "media-video/xanim";
	unsafe  = true;
	notes   = "The dexvert version of xanim has special export functionality, originally based on the loki xanim fork, but I've ehnhanced it to support other animation formats and output correctly on 32bit x11 displays";
	flags   = {
		fps : "FPS of frames. Default: 10"
	};
	bin      = "xanim";
	args     = r => ["+Ze", "+l0", "-Zr", "+Ee", r.inFile()];
	
	// We could run in cwd outDir, but some fiels like movieSetter rely on external files being in the same directory, so it's easiest to run in the default r.f.root cwd and then just move all the ppm files over afterwards
	postExec = async r => (await (await fileUtil.tree(r.f.root, {nodir : true, depth : 1, regex : /\.ppm$/i})).parallelMap(async filePath => await Deno.rename(filePath, path.join(r.outDir({absolute : true}), path.basename(filePath)))));

	// xanim plays back in real time, so if the video is longer than 3 minutes, it just will get truncated
	runOptions = ({virtualX : true, timeout : xu.MINUTE*3, killChildren : true});
	chain      = r => `*ffmpeg[fps:${r.flags.fps || 10}] -> ffmpeg`;
	renameOut  = true;
}
