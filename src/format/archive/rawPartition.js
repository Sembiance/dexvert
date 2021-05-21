"use strict";
const XU = require("@sembiance/xu");

exports.HFS_MAGICS = ["Macintosh HFS data"];

exports.meta =
{
	name  : "Raw Partition",
	magic : [/^DOS\/MBR boot sector/, ...exports.HFS_MAGICS]
};

exports.converterPriorty = state =>
{
	const dosMBRID = state.identify.find(v => v.from==="file" && v.magic.startsWith("DOS/MBR boot sector"));
	if(dosMBRID)
	{
		const startSector = (dosMBRID.magic.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
		if(startSector && (+startSector)>0)
			return [{program : "uniso", flags : {offset : (+startSector)*512}}];
	}

	return ["uniso"];
};

