import {xu} from "xu";
import {cmdUtil, fileUtil, runUtil} from "xutil";
import {XLog} from "xlog";
import {assert, path} from "std";
import {UInt8ArrayReader} from "UInt8ArrayReader";

const xlog = new XLog("info");

const argv = cmdUtil.cmdInit({
	version : "1.0.0",
	desc    : "Processes <input> as an RIFF MMM file and extracts it's contents to <outputDirPath>",
	args :
	[
		{argid : "inputFilePath", desc : "MMM file to extract", required : true},
		{argid : "outputDirPath", desc : "Output directory to extract to", required : true}
	]});

// Sources:
// https://github.com/mainframed/HACKERS.EXE/blob/main/dump_rmmp.py#L54C16-L54C28
// https://discmaster.textfiles.com/view/10255/CICA.cdr/win_nt/multimed/samples/mmpf.zip/MMPF.C

const fileSize = (await Deno.stat(argv.inputFilePath)).size;
const reader = new UInt8ArrayReader(await Deno.readFile(argv.inputFilePath), {endianness : "le"});
assert(reader.str(4)==="RIFF");
assert([fileSize, fileSize-8].includes(reader.uint32()));
assert(reader.str(4)==="RMMP");
assert(["CFTC", "cftc"].includes(reader.str(4)));	// DEMO286.MMM has all lowercase tags (except for first RIFF AND RMMP) maybe older version?

const cftcLength = reader.uint32();
assert(reader.uint32()===0);
assert((cftcLength%4)===0);

const chunks = [];

while(reader.pos+16<=cftcLength)
{
	const tag = reader.str(4);
	const length = reader.uint32();
	const seq = reader.uint32();
	const offset = reader.uint32();
	if(["CFTC", "cftc", "\0\0\0\0"].includes(tag))
		continue;
	chunks.push({tag, length, seq, offset});
}

const meta = {strs : [], vwci : {}, fonts : [], dibs : {}, stxts : []};

for(const chunk of chunks)
{
	reader.setPOS(chunk.offset);
	assert(reader.str(4)===chunk.tag);
	assert(reader.uint32()===chunk.length);
	assert(reader.uint32()===chunk.seq);
	const data = reader.sub(chunk.length-4);
	
	if(["McNm", "mcnm"].includes(chunk.tag))
	{
		data.skip(1);
		meta.name = data.str(data.remaining());
	}
	else if(["Ver.", "ver "].includes(chunk.tag))
	{
		meta.version = {seq : chunk.seq, bytes : [data.uint8(), data.uint8()]};
	}
	else if(["STR ", "str "].includes(chunk.tag))
	{
		data.skip(2);
		meta.strs.push(data.strPascal());
	}
	else if(["VWCI", "vwci"].includes(chunk.tag))
	{
		data.skip(6);
		const isScript = data.uint8()!==0;
		if(isScript)
		{
			data.skip(36);
			meta.vwci[chunk.seq] = {script : data.strPascal()};
		}
		else
		{
			data.skip(24);
			meta.vwci[chunk.seq] = {nums : [0, 1, 2].map(() => data.uint32()), other : data.strPascal()};
		}
	}
	else if(["VWAC", "vwac"].includes(chunk.tag))
	{
		data.skip(2);
		const numActions = data.uint16(true);
		data.skip(4*(numActions+1));
		data.rewind(2);
		const vwacStrLength = data.uint16(true);
		meta.vwacStr = data.str(vwacStrLength);
	}
	else if(["VWFM", "vwfm"].includes(chunk.tag))
	{
		data.skip(2);
		const numFonts = data.uint16(true);
		data.skip(2*numFonts);
		for(let i=0;i<numFonts;i++)
			meta.fonts.push(data.strPascal());
	}
	else if(["DIB ", "dib "].includes(chunk.tag))
	{
		// skip these, deark handles these
		/*data.skip(6);
		const w = data.uint32();
		const h = data.uint32();
		const colorPlanes = data.uint16();
		const bitsPerPixel = data.uint16();
		const compression = data.uint32();
		const sizeImage = data.uint32();
		const xDPI = data.uint32();
		const yDPI = data.uint32();
		const colorsUsed = data.uint32();
		const colorsImportant = data.uint32();

		meta.dibs[chunk.seq] = {w, h, colorPlanes, bitsPerPixel, compression, sizeImage, xDPI, yDPI, colorsUsed, colorsImportant};
		
		await data.writeToDisk(data.remaining(), path.join(argv.outputDirPath, `${chunk.seq}.dib`));
		xlog.info`${chunk.seq} ${w}x${h} ${sizeImage} bytes (compressed: ${compression})`;*/
	}
	else if(["SND ", "snd "].includes(chunk.tag))
	{
		const filename = data.strPascal();
		const tmpRawFilePath = await fileUtil.genTempPath(undefined, ".raw");
		await data.writeToDisk(data.remaining(), tmpRawFilePath);
		await runUtil.run("sox", ["-t", "raw", "-r", "22050", "-c", "1", "-b", "8", "-e", "unsigned", tmpRawFilePath, path.join(argv.outputDirPath, `${chunk.seq}_${filename}.wav`)]);
		await fileUtil.unlink(tmpRawFilePath);
	}
	else if(["STXT", "stxt"].includes(chunk.tag))
	{
		data.skip(8);
		const textLength = data.uint16(true);
		if(textLength)
		{
			data.skip(4);
			meta.stxts.push(data.str(textLength));
		}
	}
	else
	{
		// VWSC - Score?

		//xlog.info`[${chunk.tag}] @${chunk.offset.toString().padStart(fileSize.toString().length, " ")} ${data.length().toString().padStart(fileSize.toString().length, " ")} bytes (seq ${chunk.seq}) NOT YET SUPPORTED`;
	}

	//xlog.info`${chunk.tag} @${chunk.offset} ${data.length()} ${chunk.seq}`;
	//xlog.info`${data.arr.asHex()}`;
}

const r = [];
if(meta.name?.length)
	r.push(`Name\n----\n${meta.name}\n`);
if(meta.strs.length)
	r.push(`Strings\n------\n${meta.strs.join("\n")}\n`);
if(meta.stxts.length)
	r.push(`stxt\n----\n${meta.stxts.join("\n")}\n`);
if(meta.vwacStr?.length)
	r.push(`Script Channel Commands\n--------------------\n${meta.vwacStr}\n`);
if(Object.keys(meta.vwci).length)
	r.push(`vwci\n----\n${Object.entries(meta.vwci).map(([id, o]) => `${id}: ${o.other}`).join("\n")}\n`);
if(meta.fonts.length)
	r.push(`Fonts\n-----\n${meta.fonts.join("\n")}\n`);

await fileUtil.writeTextFile(path.join(argv.outputDirPath, "meta.txt"), r.join("\n"));
//xlog.info`${meta}`;
