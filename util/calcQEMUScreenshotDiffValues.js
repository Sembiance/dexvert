import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, runUtil} from "xutil";
import {QEMU_INSTANCE_DIR_PATH} from "../src/server/qemu.js";
import {path} from "std";

const xlog = new XLog();

const instanceJSONFilePaths = await fileUtil.tree(QEMU_INSTANCE_DIR_PATH, {nodir : true, regex : /instance\.json$/});
if(instanceJSONFilePaths.length===0)
	Deno.exit(xlog.warn`No instance JSON files found in dir: ${QEMU_INSTANCE_DIR_PATH}`);

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
	r.push({osid, instanceid, vncPort, diff : +instanceDiff.trim()});
});

await fileUtil.unlink(tmpSnapshotDirPath, {recursive : true});

console.log(JSON.stringify(r));
