import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil, printUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexrecurse",
	opts    :
	{
		sample     : {desc : "Only test a specific sample, just pass the file/dirname of the sample", hasValue : true, asString : true},
		record     : {desc : "Take the results of the conversions and save them as future expected results"}
	}});

const xlog = new XLog();

const SAMPLE_DIR_PATH = path.join(import.meta.dirname, "sample");

const samplePaths = await fileUtil.tree(SAMPLE_DIR_PATH, {depth : 1, sort : true});
if(argv.sample)
	samplePaths.filterInPlace(v => path.basename(v)===argv.sample);

if(!samplePaths.length)
	Deno.exit(xlog.error`No sample paths found!`);

async function testSample(samplePath)
{
	console.log(printUtil.minorHeader(`Testing sample: ${path.relative(SAMPLE_DIR_PATH, samplePath)}`, {prefix : "\n"}));

	const outDirPath = await fileUtil.genTempPath(undefined, `-testrecurse-${path.basename(samplePath)}`);
	await Deno.mkdir(outDirPath);

	await runUtil.run("deno", runUtil.denoArgs("dexrecurse.js", samplePath, outDirPath), runUtil.denoRunOpts({cwd : path.join(import.meta.dirname, "..", "..", "src", "app"), liveOutput : true}));
	
	xlog.info`Finished, gathering results...`;

	const expectedDirPath = path.join(import.meta.dirname, "expected", path.basename(samplePath));
	const resultFiles = await fileUtil.tree(outDirPath, {relative : true});
	if(argv.record)
	{
		xlog.info`Recording ${resultFiles.length} results to: ${expectedDirPath}`;
		await fileUtil.unlink(expectedDirPath, {recursive : true});
		await runUtil.run("rsync", runUtil.rsyncArgs(path.join(outDirPath, "/"), path.join(expectedDirPath, "/"), {fast : true}));
		return;
	}

	const expectedFiles = await fileUtil.tree(expectedDirPath, {relative : true});

	const missingFiles = expectedFiles.subtractAll(resultFiles);
	if(missingFiles.length>0)
		xlog.error`${missingFiles.length} Missing files: ${missingFiles}`;

	const extraFiles = resultFiles.subtractAll(expectedFiles);
	if(extraFiles.length>0)
		xlog.error`${extraFiles.length} Extra files: ${extraFiles}`;

	// Could possibly compare times on files, file sizes, etc

	await fileUtil.unlink(outDirPath, {recursive : true});
}

for(const samplePath of samplePaths)
	await testSample(samplePath);

xlog.info`Done!`;
