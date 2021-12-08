import {xu} from "xu";
import {cmdUtil} from "xutil";
import {path} from "std";
const xlog = xu.xLog();

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input.ilb> as an Impact Screensaver ILB archive and extracts it into <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "ILB file path to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

const buf = await Deno.readFile(argv.inputFilePath);

let pos=0;

const readNum = () =>
{
	const num = buf.getUInt32LE(pos);
	pos+=4;
	return num;
};

const archiveNameLen = readNum();
const archiveName = buf.getString(pos, archiveNameLen);
pos+=archiveNameLen;
xlog.info`Archive Name: ${archiveName}`;

const numImages = readNum();

// If num images isn't zero, then skip numImages bytes, not sure what they are
if(numImages!==0)
	pos+=numImages;

while(pos<buf.length)
{
	const filenameLen = readNum();
	const fileLen = readNum();
	const filename = buf.getString(pos, filenameLen);
	pos+=filenameLen;

	const filePath = path.join(argv.outputDirPath, filename.replaceAll("/", "-").replaceAll("..", "__"));
	xlog.info`Extracting file ${filename} that is ${fileLen} bytes in size to ${filePath}`;
	
	await Deno.writeFile(filePath, buf.subarray(pos, pos+fileLen));
	pos+=fileLen;

	// Always an extra byte at the end, seems to always be zero, maybe a padding byte
	// Also sometimes see some previous zero bytes (0 to 3) as part of fileLen, maybe they are aligning to 4-byte boundaries?
	pos++;
}
