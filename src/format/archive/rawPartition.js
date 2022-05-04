import {Format} from "../../Format.js";

const HFS_MAGICS = ["Macintosh HFS data"];

export class rawPartition extends Format
{
	name       = "Raw Partition";
	magic      = [/^DOS\/MBR boot sector/, ...HFS_MAGICS, "UDF filesystem data", /^fmt\/(468|1087|1105)( |$)/];
	converters = async dexState =>
	{
		const dosMBRID = dexState.ids.find(id => id.from==="file" && id.magic.startsWith("DOS/MBR boot sector"));
		if(dosMBRID)
		{
			const startSector = (dosMBRID.magic.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
			if(startSector && (+startSector)>0)
				return [`uniso[offset:${(+startSector)*512}]`];
		}

		const {flexMatch} = await import("../../identify.js");	// need to import this dynamically to avoid circular dependency
		const isHFS = dexState.ids.some(id => HFS_MAGICS.some(matchAgainst => flexMatch(id.magic, matchAgainst)));
		return [`uniso${isHFS ? "[hfs]" : ""}`];
	};
}
