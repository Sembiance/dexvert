import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil} from "xutil";
import {path} from "std";

const QEMU_DIR_PATH = "/mnt/dexvert/qemu";
const MAX_ALLOWABLE_QEMU_DIFFS =
{
	win2k    : 0.2,
	winxp    : 0.2,
	amigappc : 0.3
};

const xlog = new XLog();

const instanceJSONFilePaths = await fileUtil.tree(QEMU_DIR_PATH, {nodir : true, regex : /instance\.json$/, depth : 2});
if(instanceJSONFilePaths.length===0)
	Deno.exit(xlog.warn`No instance JSON files found in dir: ${QEMU_DIR_PATH}`);

const tmpSnapshotDirPath = await fileUtil.genTempPath();
await Deno.mkdir(tmpSnapshotDirPath);

const qemu = [];
await instanceJSONFilePaths.parallelMap(async instanceJSONFilePath =>
{
	const {osid, instanceid, vncPort} = xu.parseJSON(await Deno.readTextFile(instanceJSONFilePath));
	const o = {osid, instanceid, vncPort};

	// check screenshot against good baselines
	const snapshotFilePath = path.join(tmpSnapshotDirPath, `${osid}-${instanceid}.png`);
	await runUtil.run("vncsnapshot", ["-nojpeg", "-compresslevel", "0", "-vncQuality", "9", `127.0.0.1:${vncPort}`, snapshotFilePath]);
	const {stdout : instanceDiff} = await runUtil.run("puzzle-diff", [path.join(xu.dirname(import.meta), "..", "qemu", "baseline-screenshots", `${osid}.png`), snapshotFilePath]);
	await fileUtil.unlink(snapshotFilePath);
	o.diff = +instanceDiff.trim();
	if(o.diff>MAX_ALLOWABLE_QEMU_DIFFS[osid])
		o.dirty = true;

	// check in/out mapped drives for any files still hanging around, all operating systems except amiga
	if(!["amigappc"].includes(osid))
		o.orphanFileCount = (await ["in", "out"].parallelMap(async k => (await fileUtil.tree(path.join(QEMU_DIR_PATH, `${osid}-${instanceid}`, k))).length)).sum();

	qemu.push(o);
});

await fileUtil.unlink(tmpSnapshotDirPath, {recursive : true});

const garbageCount = (await fileUtil.tree("/mnt/dexvert/garbageDetected", {nodir : true}))?.length || 0;
console.log(JSON.stringify({qemu, garbageCount}));
