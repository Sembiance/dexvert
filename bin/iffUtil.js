import {xu} from "xu";
import {UInt8ArrayReader} from "UInt8ArrayReader";
import {writeAll} from "std";

// IFF spec: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF
export async function read(src)
{
	if(typeof src==="string")
		src = await Deno.readFile(src);

	const reader = new UInt8ArrayReader(src);

	const r = {};
	r.type = reader.str(4);
	r.length = reader.uint32();
	if(r.type==="FORM")
	{
		r.formType = reader.str(4);
		r.chunks = [];
		while(reader.remaining()>=8)
		{
			const chunk = {};
			chunk.type = reader.str(4);
			chunk.length = reader.uint32();
			chunk.data = reader.raw(chunk.length);
			if(chunk.length%2===1)
				reader.skip(1);
			r.chunks.push(chunk);
		}
	}
	else if(r.type==="LIST")
	{
		r.iffs = [];
		const props = {};
		for(let i=0;i<r.length;i++)
		{
			const op = reader.str(4);
			if(op==="SSET")
			{
				i--;	// SSET's don't count for the length
				const setType = reader.str(4);
				if(setType==="PROP")
				{
					const propLength = reader.uint32();

					const propType = reader.str(4);
					props[propType] ||= {};
					const chunkType = reader.str(4);
					props[propType][chunkType] = reader.raw(propLength-8);
				}
				else
				{
					throw new Error(`Unhandled SSET type: ${setType}`);
				}
			}
			else if(["FORM", "LIST", "CAT"].includes(op))
			{
				const iffLength = reader.uint32();
				reader.rewind(8);
				const iff = await read(reader.raw(iffLength+8));
				if(op==="FORM")
				{
					for(const [iffType, chunkTypes] of Object.entries(props))
					{
						for(const [chunkType, chunkData] of Object.entries(chunkTypes))
						{
							if(iff.formType!==iffType || iff.chunks.some(chunk => chunk.type===chunkType))
								continue;

							iff.chunks.unshift({type : chunkType, length : chunkData.length, data : chunkData});
						}
					}
				}

				r.iffs.push(iff);
			}
			else
			{
				throw new Error(`Unhandled LIST sub-file: ${op}`);
			}
		}
	}
	
	return r;
}

export async function write(iff, dest)
{
	if(iff.type!=="FORM")
		throw new Error(`Can only write FORM IFF files for now`);

	const encoder = new TextEncoder();
	const encodeUint32 = v =>
	{
		const a = new Uint8Array(4);
		a.setUInt32BE(0, v);
		return a;
	};

	const file = await Deno.open(dest, {create : true, write : true, truncate : true});
	await writeAll(file, encoder.encode(iff.type));
	await writeAll(file, encodeUint32(iff.length));
	await writeAll(file, encoder.encode(iff.formType));
	for(const chunk of iff.chunks)
	{
		await writeAll(file, encoder.encode(chunk.type));
		await writeAll(file, encodeUint32(chunk.length));
		await writeAll(file, chunk.data);
		if(chunk.length%2===1)
			await writeAll(file, new Uint8Array([0]));
	}
	file.close();
}
