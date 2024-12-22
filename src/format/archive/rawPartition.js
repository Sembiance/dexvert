import {Format} from "../../Format.js";

const HFS_MAGICS = ["Macintosh HFS data", "HFS file system"];

export class rawPartition extends Format
{
	name           = "Raw Partition";
	ext            = [".raw", ".hd", ".img", ".vhd"];
	forbidExtMatch = true;
	magic          = [
		/^DOS\/MBR boot sector/, ...HFS_MAGICS, "UDF filesystem data", "romfs image", "romfs filesystem", "LILO boot loader Minix file system", "Linux romfs", "LILO boot loader", "Linux/i386 LILO", "DOS/MBR partition map", "SysV file system",
		"FAT16 file system", "eXtended Density Format disk image", "LILO bootloader disk image", /^GPT partition table/, /^SYSLINUX boot loader/, /^Syslinux bootloader/, "U-Boot uImage", /^u-boot legacy uImage/, "Format: U-Boot", "uImage header",
		"XENIX file system", "System Deployment Image", "application/x-vhd-disk", "Virtual PC Virtual HD image", "Format: Microsoft Virtual Hard Disk (.VHD)", "Connectix Virtual PC hard disk image", /^Microsoft Disk Image/, "MPFS filesystem",
		/^fmt\/(468|1087|1105|1739)( |$)/
	];
	idMeta     = ({macFileType, macFileCreator}) => (["devi", "devr"].includes(macFileType) && macFileCreator==="ddsk") || (macFileType==="DDim" && macFileCreator==="DDp+");
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
			converters.push("uniso[hfsplus]", "uniso[hfs]", "deark[module:hfs]");
		else
			converters.push("uniso");
		converters.push("aaru", "sevenZip");
		return converters;
	};
}
