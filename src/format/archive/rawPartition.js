import {Format} from "../../Format.js";

const HFS_MAGICS = ["Macintosh HFS data", "HFS file system"];

export class rawPartition extends Format
{
	name       = "Raw Partition";
	magic      = [/^DOS\/MBR boot sector/, ...HFS_MAGICS, "UDF filesystem data", "romfs image", "romfs filesystem", "LILO boot loader Minix file system", "Linux romfs", "LILO boot loader", "Linux/i386 LILO", "DOS/MBR partition map", /^fmt\/(468|1087|1105|1739)( |$)/];
	converters = dexState =>
	{
		const dosMBRID = dexState.ids.find(id => id.from==="file" && id.magic.startsWith("DOS/MBR boot sector"));
		if(dosMBRID)
		{
			const startSector = (dosMBRID.magic.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
			if(startSector && (+startSector)>0)
				return [`uniso[offset:${(+startSector)*512}]`];
		}

		const isHFS = dexState.hasMagics(HFS_MAGICS);
		const converters = [`uniso${isHFS ? "[hfs]" : ""}`];
		if(isHFS)
			converters.push("deark[module:hfs]");
		return converters;
	};
}
