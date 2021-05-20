"use strict";
const XU = require("@sembiance/xu"),
	dexUtil = require("../../dexUtil.js"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file,
	runUtil = require("@sembiance/xutil").run,
	path = require("path");

const HFS_MAGICS = [...require("../../format/archive/iso.js").HFS_MAGICS, ...require("../../format/archive/rawPartition.js").HFS_MAGICS];	// eslint-disable-line node/global-require

exports.meta =
{
	website       : ["https://www.mars.org/home/rob/proj/hfs/", "https://www.sudo.ws/", "https://www.kernel.org/pub/linux/utils/util-linux/"],
	gentooPackage : ["sys-fs/hfsutils", "app-admin/sudo", "sys-apps/util-linux"],
	bin           : ["*", "sudo", "mount"]
};

exports.bin = () => path.join(__dirname, "..", "..", "..", "bin", "uniso");
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath, isoType=(state.identify.some(identification => HFS_MAGICS.some(matchAgainst => dexUtil.flexMatch(identification.magic, matchAgainst))) ? "hfs" : "")) =>
{
	const unisoArgs = [];
	r.isoType = isoType;
	if(r.flags.offset)
		unisoArgs.push(`--offset=${r.flags.offset}`);

	return ([...unisoArgs, inPath, outPath, isoType]);
};

exports.post = (state, p, r, cb) =>
{
	if(r.isoType!=="hfs")
		return setImmediate(cb);

	// If we are an Mac CD (HFS) then run every file through 'unar' which will split data and resource fork into seperate files, then remove the original
	tiptoe(
		function findOutputDirectories()
		{
			fileUtil.glob(state.output.absolute, "**/*", {nodir : true}, this);
		},
		function identifyOutputFiles(extractedFilePaths)
		{
			extractedFilePaths.parallelForEach((extractedFilePath, subcb) =>
			{
				const tmpUnpackDirPath = fileUtil.generateTempFilePath(path.dirname(extractedFilePath), "");

				tiptoe(
					function prepareTmp()
					{
						fs.mkdir(tmpUnpackDirPath, this);
					},
					function unpackIntoTmpDir()
					{
						runUtil.run("unar", ["-f", "-D", "-o", tmpUnpackDirPath, extractedFilePath], runUtil.SILENT, this);
					},
					function findUnpackedFiles()
					{
						fileUtil.glob(tmpUnpackDirPath, "*", {nodir : true}, this);
					},
					function deleteOriginal(unpackedFilePaths)
					{
						if(unpackedFilePaths.length===0)
							return this.jump(2);

						this.data.unpackedFilePaths = unpackedFilePaths;
						fileUtil.unlink(extractedFilePath, this);
					},
					function copyNewFiles()
					{
						this.data.unpackedFilePaths.parallelForEachC((unpackedFilePath, unpackcb) => fileUtil.move(unpackedFilePath, path.join(path.dirname(extractedFilePath), path.basename(unpackedFilePath.replaceAll(".adf", ".rsrc"))), unpackcb), this);
					},
					function removeTmpUnpackDir()
					{
						fileUtil.unlink(tmpUnpackDirPath, this);
					},
					subcb
				);
			}, this);
		},
		cb
	);
};
