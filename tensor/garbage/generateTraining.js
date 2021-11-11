"use strict";
/* eslint-disable max-len, node/global-require */
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	dexUtil = require("../../src/dexUtil"),
	StreamSkip = require("stream-skip"),
	dexvert = require("../../src/dexvert.js"),
	path = require("path"),
	fs = require("fs"),
	tiptoe = require("tiptoe");

console.error("This script hasn't been updated after moving it out of dexvert/util/ dir, nor after moving the training file locations. So need to update this before it can be run again.");
process.exit(1);

const NUM_PER_FORMAT = 10;
let GOOD_PNGS = [];
const tmpDirPath = "/mnt/ram/tmp";
const BAD_PNGS_DIR_PATH = path.join(__dirname, "badPNGs");

tiptoe(
	function findGoodPNGs()
	{
		fileUtil.glob(path.join(__dirname, "goodPNGs"), "*.png", {nodir : true}, this.parallel());
		dexUtil.findFormats(this.parallel());
	},
	function getFormats(goodPNGPaths, formats)
	{
		GOOD_PNGS = goodPNGPaths.map(goodPNGPath => ({size : fs.statSync(goodPNGPath).size, filePath : goodPNGPath}));

		const recoilFormats = Object.entries(formats.image).filter(([, format]) => (format.converterPriority || []).length===1 && (format.converterPriority || []).includes("recoil2png") && format.meta.fileSize);
		recoilFormats.shuffle().parallelForEach(([formatid, format], subcb) => [].pushSequence(1, NUM_PER_FORMAT).parallelForEach((i, icb) => generateForFormat(formatid, format, icb), subcb), this);
	},
	XU.FINISH
);

function generateForFormat(formatid, format, cb)
{
	const tmpFilePath = fileUtil.generateTempFilePath(tmpDirPath, format.meta.ext.pickRandom(1));
	const tmpOutDirPath = fileUtil.generateTempFilePath(tmpDirPath);
	const targetFileSize = (Object.isObject(format.meta.fileSize) ? Object.values(format.meta.fileSize).map(v => Array.force(v)) : Array.force(format.meta.fileSize)).flat().pickRandom(1)[0];
	const goodPNG = GOOD_PNGS.filter(v => v.size>targetFileSize).pickRandom(1)[0];

	tiptoe(
		function createOutDirPath()
		{
			fs.mkdir(tmpOutDirPath, this);
		},
		function createTmpFile()
		{
			const inStream = fs.createReadStream(goodPNG.filePath);
			inStream.on("error", this);
			inStream.on("end", this);
			inStream.pipe(new StreamSkip({skip : Math.randomInt(0, (goodPNG.size-targetFileSize))})).pipe(fs.createWriteStream(tmpFilePath));
		},
		function truncateFile()
		{
			fs.truncate(tmpFilePath, targetFileSize, this);
		},
		function performConversion()
		{
			dexvert.process(tmpFilePath, tmpOutDirPath, {tmpDirPath}, this);
		},
		function findOutputFiles()
		{
			fileUtil.glob(tmpOutDirPath, "**/*", {nodir : true}, this.parallel());
			fileUtil.unlink(tmpFilePath, this.parallel());
		},
		function copyOutputFiles(outputFilePaths)
		{
			process.stdout.write(".".repeat(outputFilePaths.length));
			outputFilePaths.parallelForEach((outputFilePath, subcb) => fs.copyFile(outputFilePath, path.join(BAD_PNGS_DIR_PATH, path.basename(outputFilePath)), subcb), this);
		},
		function deleteTmpFiles()
		{
			fileUtil.unlink(tmpOutDirPath, this);
		},
		cb
	);
}
