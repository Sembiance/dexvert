"use strict";
const XU = require("@sembiance/xu"),
	dexUtil = require("../../dexUtil.js");

const HFS_MAGICS = ["Macintosh HFS data"];

exports.meta =
{
	name  : "Raw Partition",
	magic : [/^DOS\/MBR boot sector/, ...HFS_MAGICS]
};

exports.converterPriority = state =>
{
	const dosMBRID = state.identify.find(v => v.from==="file" && v.magic.startsWith("DOS/MBR boot sector"));
	if(dosMBRID)
	{
		const startSector = (dosMBRID.magic.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
		if(startSector && (+startSector)>0)
			return [{program : "uniso", flags : {offset : (+startSector)*512}}];
	}

	const unisoProg = {program : "uniso"};
	if(state.identify.some(identification => HFS_MAGICS.some(matchAgainst => dexUtil.flexMatch(identification.magic, matchAgainst))))
		unisoProg.flags = {hfs : true};

	return [unisoProg];
};

