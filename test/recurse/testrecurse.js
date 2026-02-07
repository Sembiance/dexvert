import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil, printUtil} from "xutil";
import {path} from "std";
import {XLog} from "xlog";
import {C} from "../../pp/ppUtil.js";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test dexrecurse",
	opts    :
	{
		record : {desc : "Take the results of the conversions and save them as future expected results"},
		sample : {desc : "Only test a specific sample, just pass the file/dirname of the sample", hasValue : true, asString : true}
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
	const sampleDirName = path.relative(SAMPLE_DIR_PATH, samplePath);
	console.log(printUtil.minorHeader(`Testing sample: ${sampleDirName}`, {prefix : "\n"}));

	const outDirPath = await fileUtil.genTempPath(undefined, `-testrecurse-${path.basename(samplePath)}.NOSUFFIX`);
	await Deno.mkdir(outDirPath);

	const expectedDirPath = path.join(import.meta.dirname, "expected", path.basename(samplePath));
	const expectedReport = xu.parseJSON(await fileUtil.readTextFile(path.join(expectedDirPath, "report.json")));

	const itemMetaURLFilePath = await fileUtil.genTempPath(undefined, ".json");
	await fileUtil.writeTextFile(itemMetaURLFilePath, JSON.stringify(expectedReport.postProcess.item));
	await runUtil.run("deno", runUtil.denoArgs("dexrecurse.js", "--postProcess", `--itemMetaURL=file://${itemMetaURLFilePath}`, samplePath, outDirPath), runUtil.denoRunOpts({cwd : path.join(import.meta.dirname, "..", "..", "src", "app"), liveOutput : true}));
	await fileUtil.unlink(itemMetaURLFilePath);
	
	xlog.info`Finished, gathering results...`;

	await runUtil.run("find", [outDirPath, "-type", "d", "-empty", "-delete"]);
	if(argv.record)
	{
		xlog.info`Recording ${(await fileUtil.tree(outDirPath, {relative : true})).length.toLocaleString()} results to: ${expectedDirPath}`;
		await fileUtil.unlink(expectedDirPath, {recursive : true});
		await runUtil.run("rsync", runUtil.rsyncArgs(path.join(outDirPath, "/"), path.join(expectedDirPath, "/"), {fast : true}));
		return;
	}

	const resultReport = xu.parseJSON(await fileUtil.readTextFile(path.join(outDirPath, "report.json")));
	for(const key of ["finished", "handled"])
	{
		if(expectedReport[key]!==resultReport[key])
			xlog.error`Report key ${key} of ${resultReport[key]} !== ${expectedReport[key]}`;
	}

	// compare duration and if >10% difference from expected, log it
	let durationDifference = Math.abs(resultReport.duration-expectedReport.duration);
	if(durationDifference>(expectedReport.duration*0.1))
		xlog.warn`Report duration of ${resultReport.duration.msAsHumanReadable()} has difference of ${durationDifference.msAsHumanReadable()} > 10% vs expected duration of ${expectedReport.duration.msAsHumanReadable()}`;

	durationDifference = Math.abs(resultReport.postProcess.duration-expectedReport.postProcess.duration);
	if(durationDifference>(expectedReport.postProcess.duration*0.1))
		xlog.warn`Report postProcess.duration of ${resultReport.postProcess.duration.msAsHumanReadable()} has difference of ${durationDifference.msAsHumanReadable()} > 10% vs expected postProcess.duration of ${expectedReport.postProcess.duration.msAsHumanReadable()}`;

	for(const type of ["file", "web", "thumb"])
	{
		const {stdout : expectedKeysRaw} = await runUtil.run("/mnt/compendium/bin/sparkeyListKeys", [path.join(expectedDirPath, `${sampleDirName}_${type}`)]);
		const expectedKeys = expectedKeysRaw.trim().split("\n").filter(v => v?.length);
		const {stdout : resultKeysRaw} = await runUtil.run("/mnt/compendium/bin/sparkeyListKeys", [path.join(outDirPath, `${sampleDirName}_${type}`)]);
		const resultKeys = resultKeysRaw.trim().split("\n").filter(v => v?.length);
		const missingKeys = expectedKeys.subtractAll(resultKeys);
		if(missingKeys.length>0)
			xlog.error`${missingKeys.length.toLocaleString()} Missing ${type} sparkey keys:\n\t${missingKeys.join("\n\t")}`;

		const extraKeys = resultKeys.subtractAll(expectedKeys);
		if(extraKeys.length>0)
			xlog.error`${extraKeys.length.toLocaleString()} Extra ${type} sparkey keys:\n\t${extraKeys.join("\n\t")}`;
	}

	const totalBytesDifference = Math.abs(resultReport.postProcess.totalBytes-expectedReport.postProcess.totalBytes);
	if(totalBytesDifference>(expectedReport.postProcess.totalBytes*0.1))
		xlog.warn`Report postProcess.totalBytes of ${resultReport.postProcess.totalBytes.bytesToSize()} has difference of ${totalBytesDifference.bytesToSize()} > 10% vs expected postProcess.totalBytes of ${expectedReport.postProcess.totalBytes.bytesToSize()}`;

	for(const key of ["handledCount", "fileCount", "indexedCount"])
	{
		if(expectedReport.postProcess[key]!==resultReport.postProcess[key])
			xlog.error`Report postProcess key ${key} of ${resultReport.postProcess[key].toLocaleString()} !== ${expectedReport.postProcess[key].toLocaleString()}`;
	}

	for(const type of C.FAMILY)
	{
		if(expectedReport.postProcess.familyCounts[type]!==resultReport.postProcess.familyCounts[type])
			xlog.error`Report postProcess.familyCounts[${type}] of ${resultReport.postProcess.familyCounts[type].toLocaleString()} !== ${expectedReport.postProcess.familyCounts[type].toLocaleString()}`;
	}

	const expectedIndex = {};
	await fileUtil.readJSONLFile(path.join(expectedDirPath, `${sampleDirName}.jsonl.gz`), o =>
	{
		expectedIndex[o.fileid] = o;
	});

	let resultIndexCount = 0;
	await fileUtil.readJSONLFile(path.join(outDirPath, `${sampleDirName}.jsonl.gz`), o =>
	{
		resultIndexCount++;
		if(!expectedIndex[o.fileid])
			return xlog.error`Result index file has unexpected entry: ${o}`;

		for(const key of ["cat", "genre", "unsupported", "name", "ext", "family", "format", "width", "height", "size", "b3sum", "itemid", "animated", "nsfw", "duration"])
		{
			if(expectedIndex[o.fileid][key]!==o[key])
				return xlog.error`Result index file entry ${o.fileid} has unexpected value for key ${key}: ${o[key]} !== ${expectedIndex[o.fileid][key]}`;
		}

		const expectedTextContent = (expectedIndex[o.fileid].textContent || []).join(" ");
		if(expectedTextContent?.length && expectedTextContent!==(o.textContent || []).join(" "))
			return xlog.error`Result index file entry ${o.fileid} has unexpected textContent: ${(o.textContent || []).join(" ")} !== ${expectedTextContent}`;

		for(const key of ["v", "va"])
		{
			if(expectedIndex[o.fileid][key]?.length && expectedIndex[o.fileid][key].length!==o[key]?.length)
				return xlog.error`Result index file entry ${o.fileid} has unexpected length for key ${key}: ${o[key]?.length} !== ${expectedIndex[o.fileid][key]?.length}`;
		}
	});

	if(resultIndexCount!==Object.keys(expectedIndex).length)
		xlog.error`Result index file has ${resultIndexCount.toLocaleString()} !== ${Object.keys(expectedIndex).length.toLocaleString()} expected`;

	await fileUtil.unlink(outDirPath, {recursive : true});
}

for(const samplePath of samplePaths)
	await testSample(samplePath);

xlog.info`Done!`;
