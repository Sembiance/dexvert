import {xu} from "xu";
import {XLog} from "xlog";
import {fileUtil, cmdUtil} from "xutil";
import {path, writeAll} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Splits apart concatenated DOS EXEs",
	opts    :
	{
		logLevel : {desc : "What level to use for logging. Valid: none fatal error warn info debug trace. Default: warn", defaultValue : "info"}
	},
	args :
	[
		{argid : "inputFilePath", desc : "DOS backup file to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const xlog = new XLog(argv.logLevel);

// file format: http://fileformats.archiveteam.org/wiki/MS-DOS_EXE
const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
let exeCount = 0;
const encoder = new TextEncoder();

const encodeUint16 = v =>
{
	const a = new Uint8Array(2);
	a.setUInt16LE(0, v);
	return a;
};

while(reader.remaining())
{
	xlog.info`${reader.pos}`;
	const signature = reader.str(2);
	if(signature!=="MZ")
	{
		for(let i=0;i<exeCount;i++)
			await fileUtil.unlink(path.join(argv.outputDirPath, `${i.toString().padStart(4, "0")}.exe`));
		Deno.exit(xlog.error`Invalid DOS EXE file header in ${argv.inputFilePath} at pos ${reader.pos-2} after splitting ${exeCount} exes."`);
	}

	const lastPageBytes = reader.uint16();
	const numPages = reader.uint16();
	const exeData = reader.raw((((numPages-1)*512)+(lastPageBytes || 512))-6);

	// WARNING: DOES NOT SUPPORT OVERLAY DATA, NO RELIABLE WAY TO DETERMINE HOW MUCH THERE ACTUALLY IS
	/*let overlayData;
	if(reader.remaining())
	{
		const nextSignaturePOS = reader.sub(reader.remaining(), true).arr.indexOfX("MZ");
		if(nextSignaturePOS>0)
		{
			xlog.info`${{nextSignaturePOS}}`;
			overlayData = reader.raw(nextSignaturePOS);
		}
	}*/

	const exeFilePath = path.join(argv.outputDirPath, `${(exeCount++).toString().padStart(4, "0")}.exe`);
	const outputFile = await Deno.open(exeFilePath, {create : true, write : true, truncate : true});
	await writeAll(outputFile, encoder.encode(signature));
	await writeAll(outputFile, encodeUint16(lastPageBytes));
	await writeAll(outputFile, encodeUint16(numPages));
	await writeAll(outputFile, exeData);
	//if(overlayData)
	//	await writeAll(outputFile, overlayData);
	outputFile.close();
}

if(exeCount===1)
{
	// If we only found one EXE, then it is likely that the input file was not a concatenated EXE
	await fileUtil.unlink(path.join(argv.outputDirPath, "0000.exe"));
	Deno.exit(xlog.warn`Input file ${argv.inputFilePath} does not appear to be a concatenated DOS EXE, only 1 EXE found`);
}
