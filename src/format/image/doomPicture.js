import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {UInt8ArrayReader} from "UInt8ArrayReader";

export class doomPicture extends Format
{
	name         = "Doom Picture Format";
	website      = "https://doomwiki.org/wiki/Picture_format";
	ext          = [".titlepic", ".interpic"];
	filename     = [/^(inter|title)pic$/i];
	customMatch  = async ({inputFile, otherFiles, xlog}) =>
	{
		// look for any PNAMES or *.PNAMES files and see if our input file is in there, if so, it's a doom picture
		const pnamesFiles = otherFiles.filter(o => (o.base.toLowerCase()==="pnames" || o.ext.toLowerCase()===".pnames") && o.size>4 && o.size<xu.MB);
		for(const pnamesFile of pnamesFiles)
		{
			const numEntries = (await fileUtil.readFileBytes(pnamesFile.absolute, 4)).getUInt32LE(0);
			if(pnamesFile.size<((numEntries*8)+4))
				return false;
			
			const reader = new UInt8ArrayReader(await fileUtil.readFileBytes(pnamesFile.absolute, (numEntries*8), 4));
			for(let i=0;i<numEntries;i++)
			{
				const entryName = reader.str(8).trimChars("\0").toLowerCase();
				if(inputFile.base.toLowerCase()===entryName || inputFile.ext.toLowerCase()===`.${entryName}`)
					return true;
			}
		}

		return false;
	};
	converters = ["doomPicture2PPM"];
}
