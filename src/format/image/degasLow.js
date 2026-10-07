import {xu} from "xu";
import {Format} from "../../Format.js";

export class degasLow extends Format
{
	name       = "Degas Low Resolution Picture";
	website    = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext        = [".pc1"];
	mimeType   = "image/x-pc1";
	magic      = ["DEGAS low-res compressed bitmap", "Degas (Low Resolution - RLE) :degas:"];
	idCheck    = inputFile => inputFile.size>=32 && inputFile.size<=xu.KB*256;
	byteCheck  = [{offset : 0, match : [0x80, 0x00]}];
	converters = ["recoil2png[format:PC1]", "wuimg[format:degas][hasExtMatch]", `abydosconvert[format:${this.mimeType}]`, "nconvert[format:degas]"];
	verify     = async ({inputFile, meta}) =>
	{
		if(meta.colorCount<=1)
			return false;

		// if we have the proper extension, skip further validation, just in case the vibe coded validation below isn't 100% up to snuff
		if(inputFile.ext.toLowerCase()===".pc1")
			return true;

		const data = await Deno.readFile(inputFile.absolute);
		
		// vibe coded section
		let offset = 34;
		let decoded = 0;

		// Count complete packets until a full screen or the first structural error.
		// The detector continues for diagnostics; its boolean result depends only on this valid prefix, so stopping at the first error is equivalent.
		while(decoded<32000 && offset<data.length)
		{
			const control = data[offset++];
			if(control===0x80)
				continue; // PackBits no-op: consumes no operand.

			const count = control<0x80 ? control+1 : 257-control;
			const inputBytes = control<0x80 ? count : 1;
			if(offset+inputBytes>data.length || (decoded%40)+count>40)
				break;

			offset += inputBytes;
			decoded += count;
		}

		// Exactly 800 independently packed 40-byte plane rows form one screen.
		if(decoded===32000)
			return true;

		// Corpus-derived recovery rule: >=128 valid plane rows, plausible palette, and a modest file size. Preserve the seven reviewed damaged images.
		if(decoded<(128*40) || data.length>64066)
			return false;
		
		for(let offset=2;offset<34;offset+=2)	// eslint-disable-line no-shadow
		{
			// Big-endian palette words: (word & 0xF000) must be zero.
			if((data[offset]&0xF0)!==0)	// eslint-disable-line no-bitwise
				return false;
		}

		return true;
	};
	classify = true;
}
