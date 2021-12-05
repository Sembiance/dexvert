import {xu} from "xu";
import {runUtil, fileUtil} from "xutil";
import {path} from "std";

const tmpDirPath = await fileUtil.genTempPath();
await Deno.mkdir(tmpDirPath);
await Deno.copyFile("/mnt/compendium/DevLab/dexvert/test/sample/music/mod/MAIN2.SPD", path.join(tmpDirPath, "in.mod"));

await [].pushSequence(1, 12).parallelMap(async i =>
{
	const outPath = path.join(tmpDirPath, `out${i}`);
	await Deno.mkdir(outPath);
	await runUtil.run("xmp", ["-o", `out${i}/out.wav`, "in.mod"], {liveOutput : true, cwd : tmpDirPath});
	
	//const p = Deno.run({cmd : ["xmp", "-o", `out${i}/out.wav`, "in.mod"], cwd : tmpDirPath, stdout : "null", stderr : "null", stdin : "null"});
	//console.log(`a${i}`);
	//const r = await p.status();
	//console.log(`b${i}`, r);
});
