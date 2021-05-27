"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	printUtil = require("@sembiance/xutil").print,
	C = require("../src/C.js"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

const tmpSnapshotDirPath = fileUtil.generateTempFilePath();

tiptoe(
	function findInstanceJSONs()
	{
		fileUtil.glob(C.QEMU_INSTANCE_DIR_PATH, "*/instance.json", {nodir : true}, this.parallel());
		fs.mkdir(tmpSnapshotDirPath, this.parallel());
	},
	function readInstanceJSONs(instanceJSONFilePaths)
	{
		if(instanceJSONFilePaths.length===0)
			return XU.log`No instance JSON files found.`, this.finish();

		instanceJSONFilePaths.parallelForEach((instanceJSONFilePath, subcb) => fs.readFile(instanceJSONFilePath, XU.UTF8, subcb), this);
	},
	function takeScreenshots(instanceJSONsRaw)
	{
		this.data.instances = instanceJSONsRaw.map(instanceJSONRaw => JSON.parse(instanceJSONRaw));
		this.data.instances.parallelForEach((instance, subcb) =>
		{
			runUtil.run("vncsnapshot", ["-nojpeg", "-compresslevel", "0", "-vncQuality", "9", `127.0.0.1:${instance.vncPort}`, path.join(tmpSnapshotDirPath, `${instance.osid}-${instance.instanceid}.png`)], runUtil.SILENT, subcb);
		}, this);
	},
	function compareScreenshotsToBaselines()
	{
		this.data.instances.parallelForEach((instance, subcb) =>
		{
			runUtil.run("puzzle-diff", [path.join(__dirname, "..", "qemu", "baseline-screenshots", `${instance.osid}.png`), path.join(tmpSnapshotDirPath, `${instance.osid}-${instance.instanceid}.png`)], runUtil.SILENT, subcb);
		}, this);
	},
	function outputDiffs(instanceDiffs)
	{
		const outputData = this.data.instances.map(({osid, instanceid, vncPort}, i) => ({osid, instanceid, vncPort, diff : +instanceDiffs[i].trim()}));
		if(process.argv.slice(2).includes("--keep"))
		{
			XU.log`Screenshots saved in: ${tmpSnapshotDirPath}\n`;
			console.log(printUtil.columnizeObjects(outputData));
			this();
		}
		else
		{
			console.log(JSON.stringify(outputData));
			fileUtil.unlink(tmpSnapshotDirPath, this);
		}
	},
	XU.FINISH
);
