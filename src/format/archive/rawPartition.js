import {Format} from "../../Format.js";

const HFS_MAGICS = ["Macintosh HFS data", "HFS file system"];

export class rawPartition extends Format
{
	name           = "Raw Partition";
	ext            = [".raw", ".hd", ".img", ".vhd"];
	forbidExtMatch = true;
	magic          = [
		...HFS_MAGICS,
		/^(FAT16|Minix|MPFS|romfs|SGI XFS|SysV|UDF|XENIX|XFS) file ?system/,
		/^(LILO|SYSLINUX|Syslinux) boot ?loader/,
		"romfs image", "Linux romfs", "Linux/i386 LILO", "DOS/MBR partition map",	"eXtended Density Format disk image", /^GPT partition table/, "U-Boot uImage", /^u-boot legacy uImage/, "Format: U-Boot", "uImage header", "System Deployment Image",
		"application/x-vhd-disk", "Virtual PC Virtual HD image", "Format: Microsoft Virtual Hard Disk (.VHD)", "Connectix Virtual PC hard disk image", /^Microsoft Disk Image/, /^DOS\/MBR boot sector/,
		/^fmt\/(468|1087|1105|1609|1739)( |$)/
	];
	idMeta = ({macFileType, macFileCreator}) =>
		(["devi", "devr", "pcHD"].includes(macFileType) && macFileCreator==="ddsk") ||
		(macFileType==="DDim" && macFileCreator==="DDp+") ||
		(macFileType==="PCHD" && ["PCXT", "SWIN"].includes(macFileCreator)) ||
		(macFileType==="hdrv" && macFileCreator==="Wrap");
	metaProvider = ["parted"];
	converters = dexState =>
	{
		const dosMBRID = dexState.ids.find(id => id.from==="file" && id.magic.startsWith("DOS/MBR boot sector"));
		if(dosMBRID)
		{
			const startSector = (dosMBRID.magic.match(/startsector (?<startSector>\d+)/) || {groups : {}}).groups.startSector;
			if(startSector && (+startSector)>0)
				return [`uniso[offset:${(+startSector)*512}]`, "sevenZip"];
		}

		const isHFS = dexState.hasMagics(HFS_MAGICS);
		const converters = [];
		if(isHFS)
		{
			const firstHFSPlusPartition = (dexState.phase?.meta?.partitions || []).find(o => ["hfsx", "hfs+"].includes(o.filesystem));
			if(firstHFSPlusPartition)
				converters.push(`hfsexplorer[partition:${firstHFSPlusPartition.number-1}]`);
			
			converters.push("uniso[hfs]", "deark[module:hfs]");
		}
		else
		{
			converters.push("uniso");
		}
		converters.push("aaru", "sevenZip");
		return converters;
	};
}
