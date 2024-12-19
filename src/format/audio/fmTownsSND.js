import {xu} from "xu";
import {fileUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {Format} from "../../Format.js";

export class fmTownsSND extends Format
{
	name           = "FM-Towns SND";
	website        = "https://wiki.multimedia.cx/index.php/FM_TOWNS_SND";
	ext            = [".snd"];
	forbidExtMatch = true;
	magic          = ["FM-Towns SND"];
	weakMagic      = true;
	meta           = async inputFile =>
	{
		const header = await fileUtil.readFileBytes(inputFile.absolute, 32);
		return {name : (new UInt8ArrayReader(header)).strNullTerminated(), rate : (header.getUInt16LE(24) * 1000)/98};
	};
	converters = dexState => [`dd[bs:32][skip:1] -> sox[type:raw][rate:${dexState.meta.rate}][channels:1][bits:8][encoding:signed][endianness:little]`];
	// sox -t raw -r 20000 -e signed --endian little -b 8 -c 1 data2.raw data2_a.wav
	unsupported = true;
	notes       = "Was kinda able to convert with SOX as RAW 8-bit mono PCM, but there is a lot of static and garbled-ness and some don't sound right at all. More infoo in: https://github.com/Sembiance/dexvert/issues/25";
}
