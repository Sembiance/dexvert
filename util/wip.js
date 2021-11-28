import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path} from "std";

const OUTDIR_PATH = "/home/sembiance/tmp/out/";
const HOMEDIR_PATH = "/home/sembiance/tmp/home/";

await fileUtil.unlink(OUTDIR_PATH, {recursive : true});
await Deno.mkdir(OUTDIR_PATH);

await fileUtil.unlink(HOMEDIR_PATH, {recursive : true});
await Deno.mkdir(HOMEDIR_PATH);

const runOptions =
{
	cwd     : path.dirname(OUTDIR_PATH),
	verbose : true,
	env     :
	{
		HOME : "/mnt/ram/tmp/3008_1image-theDraw/home"
	}
};
const r = await runUtil.run("abydosconvert", ["--png", "--json", "image/x-thedraw", "in.td", OUTDIR_PATH], runOptions);
console.log({r});
