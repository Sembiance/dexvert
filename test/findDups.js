import {xu, fg} from "xu";
import {XLog} from "xlog";
import {cmdUtil, hashUtil, fileUtil, runUtil, printUtil} from "xutil";
import {path} from "std";

const xlog = new XLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Test multiple formats, creating a report for each",
	opts    :
	{
		family : {desc : "Restrict dup checks to a specific family", hasValue : true}
	}});

const srcSampleDirPath = path.join(import.meta.dirname, "sample", argv.family || "");
const localSampleDirPath = path.join("/mnt/dexvert/sample", argv.family || "");

xlog.info`Rsyncing sample files to local disk...`;
await runUtil.run("rsync", ["--delete", "-savL", path.join(srcSampleDirPath, "/"), path.join(localSampleDirPath, "/")]);

xlog.info`Finding sample files...`;
const sampleFilePaths = await fileUtil.tree(localSampleDirPath, {nodir : true});

xlog.info`Calculating hashes for ${sampleFilePaths.length} files...`;
let i=0;
const hashesByFile = Object.fromEntries(await sampleFilePaths.parallelMap(async sampleFilePath =>
{
	const r = [sampleFilePath, await hashUtil.hashFile("blake3", sampleFilePath)];
	printUtil.stdoutWrite(".");
	// Now write out every 10% of the way
	if(++i%Math.floor(sampleFilePaths.length/10)===0)
		printUtil.stdoutWrite(fg.yellow(`${Math.round(i/sampleFilePaths.length*100)}%`));
		
	return r;
}));

xlog.info`\n\nNOTE! Some duplicates are on purpose to test different filename/extension matching.\nSo delete duplicates ${fg.peach("WITH CARE")}\n`;

const filesByHash = {};
for(const [filePath, hash] of Object.entries(hashesByFile))
{
	filesByHash[hash] ||= [];
	filesByHash[hash].push(filePath);
}

for(const [, filePaths] of Object.entries(filesByHash))
{
	if(filePaths.length===1)
		continue;

	xlog.info`File duplicated ${filePaths.length} times:`;
	for(const filePath of filePaths)
		xlog.info`\t${filePath}`;
}
