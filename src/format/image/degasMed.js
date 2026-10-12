import {xu} from "xu";
import {Format} from "../../Format.js";

export class degasMed extends Format
{
	name      = "Degas Medium Resolution Picture";
	website   = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext       = [".pc2"];
	mimeType  = "image/x-pc2";
	magic     = ["DEGAS med-res compressed bitmap", "Degas (Medium Resolution - RLE) :degas:"];
	idCheck    = inputFile => inputFile.size>=34 && inputFile.size<=xu.KB*312;
	byteCheck = [{offset : 0, match : [0x80, 0x01]}];

	// nconvert & wuimg properly handles aspect ratio
	converters = ["nconvert[format:degas]", "wuimg[format:degas][hasExtMatch]", `abydosconvert[format:${this.mimeType}]`, "recoil2png[format:PC2]"];
	verify     = async ({inputFile, meta}) =>
	{
		// too many things begin with 0x8001 so we further validate here
		if(meta.colorCount<=1)
			return false;

		const data = await Deno.readFile(inputFile.absolute);
		
		// vibe coded section
		let offset = 34;
		let decoded = 0;
		
		while(decoded<32000 && offset<data.length)
		{
			const control = data[offset++];
			if(control===128)	// PackBits no-op
				continue;
		
			const count = control<128 ? control+1 : 257-control;
			const consumed = control<128 ? count : 1;
			if((offset+consumed)>data.length || (decoded%80)+count>80)
				break;
			
			offset += consumed;
			decoded += count;
		}

		// 640 pixels / 8 = 80 bytes per plane row; 2 planes * 200 rows = 32000.
		if(decoded===32000)
			return true;

		// ight scanlines of valid packets, a clean STE-compatible palette, and a modest size
		if(decoded<1280 || data.length>64066)
			return false;
		
		for(let i=2;i<34;i+=2)
		{
			if(data[i]&0xF0)	// eslint-disable-line no-bitwise
				return false;
		}

		return true;
	};
	classify = true;
}
