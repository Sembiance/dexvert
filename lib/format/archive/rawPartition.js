"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name  : "Raw Partition",
	magic : [/^DOS\/MBR boot sector/]
};

exports.converterPriorty = ["uniso"];

exports.converterPriorty = state =>
{
	const dosMBRID = state.identify.find(v => v.from==="file" && v.magic.startsWith("DOS/MBR boot sector"));
	if(dosMBRID)
	{
		const startSector = (dosMBRID.magic.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
		XU.log`startSector ${startSector}`;
		if(startSector && (+startSector)>0)
			return [{program : "uniso", flags : {offset : (+startSector)*512}}];
	}

	return ["uniso"];
};

//exports.converterPriorty = state => ((state.input.meta.ansiArt || state.input.meta.binaryText) ? ["deark", {program : "ansilove", flags : {ansiloveType : "bin"}}, "abydosconvert", "ffmpeg"] : []);

/*
		if(this.data.isRawDiskImage)
		{
			const startSector = (isoInfo.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
			if(startSector && (+startSector)>0)
			{
				runMount(["-o", `loop,offset=${(+startSector)*512}`, ISO_FILE_PATH, MOUNT_DIR_PATH], RUN_OPTIONS, err => this.jump(5, err));
				return;
			}
		}

*/
