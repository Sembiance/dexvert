import {xu} from "xu";
import {cmdUtil, runUtil, fileUtil} from "xutil";
import {XLog} from "xlog";
import {path} from "std";

const xlog = new XLog("info");

// Mac file type 'FSSD' is created by a couple different programs, but usually it's SoundEdit
// It has a data fork which the PCM raw data is in and also an INFO resource #1000 that has info about the sound: https://macgui.com/usenet/?group=21&start=360&id=458
// Other info on the format: http://www-cs-students.stanford.edu/~franke/SoundApp/formats.html

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Converts <input> from mac FSSD sound to 1 or 2 wavs in outputDirPath",
	opts :
	{
		debug : {desc : "Debug mode"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "FSSD file path to convert", required : true},
		{argid : "outputDirPath", desc : "Output dir to write to", required : true}
	]});

const RATES =
{
	1 : 22256,
	2 : 11128,
	3 : 7418,
	4 : 5564
};

const wipDirPath = await fileUtil.genTempPath(undefined, "ffsd2wav");
await Deno.mkdir(wipDirPath, {recursive : true});

// first seperate the rsrc and data forks
await runUtil.run("unar", ["-f", "-D", "-o", wipDirPath, argv.inputFilePath]);

async function cleanupAndExit(ignored)
{
	if(argv.debug)
		xlog.info`wipDirPath: ${wipDirPath}`;
	else
		await fileUtil.unlink(wipDirPath, {recursive : true});
	Deno.exit();
}

async function convertFileToWav(inputFilePath, rate, channelCount, suffix="")
{
	const fileBase = path.basename(inputFilePath).replace(/^out\.\d{3}./, "");
	await runUtil.run("sox", ["-t", "raw", "-r", rate.toString(), "-e", "unsigned", "-b", "8", "-c", channelCount.toString(), inputFilePath, path.join(argv.outputDirPath, `${fileBase}${suffix}.wav`)]);
}

// find the rsrc and data forks
let outputFiles = await fileUtil.tree(wipDirPath, {nodir : true});

if(!outputFiles.length)
{
	// sometimes unar can't extract it, usually due to some minor corruption in the file, so let's try using deark
	await runUtil.run("deark", ["-m", "macbinary", "-od", wipDirPath, "-d", "-o", "out", argv.inputFilePath]);
	outputFiles = await fileUtil.tree(wipDirPath, {nodir : true});
	const adfFilePath = outputFiles.find(v => v.toLowerCase().endsWith(".adf"));
	if(adfFilePath)
	{
		await runUtil.run("deark", ["-opt", "applesd:extractrsrc=1", "-od", wipDirPath, "-o", "out", adfFilePath]);
		await fileUtil.unlink(adfFilePath);
		outputFiles = await fileUtil.tree(wipDirPath, {nodir : true});
	}
}
const rawFilePath = outputFiles.find(v => ![".adf", ".rsrc"].some(ext => v.toLowerCase().endsWith(ext)));

if(outputFiles.length!==2)
{
	if(outputFiles.length!==1)
		await cleanupAndExit(xlog.error`Error: Expected 2 files in the unar output, but got ${outputFiles.length}`);

	if(!rawFilePath)
		await cleanupAndExit(xlog.error`Error: Expected 2 files in the unar output, but got just 1 .rsrc file`);

	xlog.warn`Warning: Expected 2 files in the unar output, but got 1, trying to convert the file with defaults`;
	await convertFileToWav(rawFilePath, RATES[1], 1, "_22kHz");
	await convertFileToWav(rawFilePath, RATES[2], 1, "_11kHz");
	await cleanupAndExit();
}

const rsrcWrappedFilePath = outputFiles.find(v => path.extname(v).toLowerCase()===".rsrc");
const dataFilePath = outputFiles.find(v => v!==rsrcWrappedFilePath);
if([".rsrc", ".adf"].some(ext => dataFilePath.toLowerCase().endsWith(ext)))
	await cleanupAndExit(xlog.error`Error: Expected just 1 .rsrc file but found 2`);

// extract our the resource keys
await runUtil.run("deark", ["-opt", "applesd:extractrsrc=1", "-od", wipDirPath, "-o", "out", rsrcWrappedFilePath]);
const rsrcFilePath = path.join(wipDirPath, "out.000.bin.rsrc");
await runUtil.run("resource_dasm", ["--skip-external-decoders", "--image-format=png", "--data-fork", rsrcFilePath, wipDirPath]);

outputFiles = await fileUtil.tree(wipDirPath, {nodir : true});

// If we have an INFO #1000 resource, grab the rate and channel count from that, otherwise we just fallback to a default, which is wrong 50% of the time
const infoFilePath = outputFiles.find(v => v.endsWith("_INFO_1000.bin"));
if(infoFilePath)
{
	// Info on the format from: https://macgui.com/usenet/?group=21&start=360&id=458
	const infoData = await Deno.readFile(infoFilePath);
	const channelNum = infoData.getUInt32BE(20);
	if(channelNum>1)
		await cleanupAndExit(xlog.error`Error: Expected channelNum at offset 20 in INFO resource to be 0 or 1, but got ${channelNum}`);

	const rateNum = infoData.getUInt32BE(28);
	if(rateNum<1 || rateNum>4)
		await cleanupAndExit(xlog.error`Error: Expected rateNum at offset 28 in INFO resource to be between 1 and 4, but got ${rateNum}`);

	await convertFileToWav(dataFilePath, RATES[rateNum], channelNum===1 ? 2 : 1);
}
else
{
	await convertFileToWav(rawFilePath, RATES[1], 1, "_22kHz");
	await convertFileToWav(rawFilePath, RATES[2], 1, "_11kHz");
}

await cleanupAndExit();
