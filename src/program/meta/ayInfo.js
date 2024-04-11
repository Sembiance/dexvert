import {xu} from "xu";
import {Program} from "../../Program.js";
import {UInt8ArrayReader} from "UInt8ArrayReader";

export class ayInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/";
	exec    = async r =>
	{
		// From: file:///mnt/compendium/DevLab/dexvert/bin/Ay_Emul29.src/HELP/html/ay_en_fmt_ay.htm
		const reader = new UInt8ArrayReader(await Deno.readFile(r.inFile({absolute : true})), {endianness : "be"});
		if(reader.str(4)!=="ZXAY")
			return;

		if(!["EMUL", "AMAD", "ST11"].includes(reader.str(4)))
			return;

		const meta = {};
		reader.skip(4);

		const authorOffset = reader.pos + reader.uint16();
		const miscOffset = reader.pos + reader.uint16();
		meta.trackCount = reader.uint8()+1;
		reader.skip(1);

		const songOffset = reader.pos + reader.uint16();

		reader.setPOS(authorOffset);
		meta.author = reader.strNullTerminated();

		reader.setPOS(miscOffset);
		meta.comment = reader.strNullTerminated();

		reader.setPOS(songOffset);
		const songTitleOffsets = [];
		for(let i=0;i<meta.trackCount;i++)
		{
			songTitleOffsets.push(reader.pos + reader.uint16());
			reader.skip(2);
		}

		meta.titles = songTitleOffsets.map(offset => { reader.setPOS(offset); return reader.strNullTerminated(); });
		
		Object.assign(r.meta, meta);
	};
	renameOut = false;
}
