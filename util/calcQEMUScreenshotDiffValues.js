import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

const MAX_ALLOWABLE_QEMU_DIFFS =
{
	win2k    : 0.2,
	winxp    : 0.2,
	amigappc : 0.3
};

const xlog = new XLog();

const instanceJSONFilePaths = await fileUtil.tree("/mnt/dexvert/qemu", {nodir : true, regex : /instance\.json$/, depth : 2});
if(instanceJSONFilePaths.length===0)
	Deno.exit(xlog.warn`No instance JSON files found in dir: /mnt/dexvert/qemu`);

const tmpSnapshotDirPath = await fileUtil.genTempPath();
await Deno.mkdir(tmpSnapshotDirPath);

const r = [];
await instanceJSONFilePaths.parallelMap(async instanceJSONFilePath =>
{
	const {osid, instanceid, vncPort} = xu.parseJSON(await Deno.readTextFile(instanceJSONFilePath));
	const snapshotFilePath = path.join(tmpSnapshotDirPath, `${osid}-${instanceid}.png`);
	await runUtil.run("vncsnapshot", ["-nojpeg", "-compresslevel", "0", "-vncQuality", "9", `127.0.0.1:${vncPort}`, snapshotFilePath]);
	const {stdout : instanceDiff} = await runUtil.run("puzzle-diff", [path.join(xu.dirname(import.meta), "..", "qemu", "baseline-screenshots", `${osid}.png`), snapshotFilePath]);
	await fileUtil.unlink(snapshotFilePath);
	const o = {osid, instanceid, vncPort, diff : +instanceDiff.trim()};
	if(o.diff>MAX_ALLOWABLE_QEMU_DIFFS[osid])
		o.dirty = true;
	r.push(o);
});

await fileUtil.unlink(tmpSnapshotDirPath, {recursive : true});

console.log(JSON.stringify(r));
