import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {path} from "std";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Checks <inputFilePath> and determines if it is a photo-cd or not",
	args :
	[
		{argid : "inputFilePath", desc : "File path to identify", required : true}
	]});

const MOUNT_DIR_PATH = await fileUtil.genTempPath(undefined, "-photocd-info");
await Deno.mkdir(MOUNT_DIR_PATH);

// fuseiso does a pretty good job at mounting photo cds, so use it to see if a photo_cd is detected
await runUtil.run("fuseiso", [argv.inputFilePath, MOUNT_DIR_PATH]);

const pcdFilePaths = await fileUtil.tree(path.join(MOUNT_DIR_PATH, "photo_cd", "images"), {nodir : true, regex : /\.pcd/i});
if((pcdFilePaths.length || [])>0)
	console.log(JSON.stringify({photocd : true, photoCount : pcdFilePaths.length}));

await runUtil.run("fusermount", ["-u", MOUNT_DIR_PATH], runUtil.SILENT, this);
await fileUtil.unlink(MOUNT_DIR_PATH, {recursive : true});
