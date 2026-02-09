import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil, runUtil} from "xutil";
import {DexFile} from "../../DexFile.js";
import {Program} from "../../Program.js";
import {path, base64Encode} from "std";
import {XLog} from "xlog";
import {_DMG_DISK_IMAGE_MAGIC} from "./dmg.js";
import {_NULL_BYTES_MAGIC} from "../other/nullBytes.js";
import {_APPLE_DISK_COPY_MAGIC} from "./appleDiskCopy.js";

// NOTE: This isn't strictly 'just ISO files'. There are some disk images in here too because the converters are the same, but technically those should probably be in rawPartition.js but meh

const MFS_MAGICS = ["MFS file system", /^Macintosh MFS data/];
const HFS_MAGICS = ["Apple ISO9660/HFS hybrid CD image", /^Apple Driver Map.*Apple_HFS/, "PC formatted floppy with no filesystem", "High Sierra CD-ROM", "HFS+ / Mac OS Extended disk image", "deark: apm",
	/^Apple HFS Plus/, /^HFS Plus/, "Apple Partition Map (APM) disk image", "Apple partition map,", /^fmt\/1757( |$)/
];

const _RAW_MAGICS = [/^Raw CD image, Mode [12]/, "deark: cd_raw"];

async function validCUEFile(dexState, cueFile)
{
	const cueInfoR = await Program.runProgram("cueInfo", cueFile, {xlog : dexState.xlog.atLeast("debug") ? dexState.xlog : new XLog("none"), autoUnlink : true});
	return (cueInfoR.meta?.files || []).filter(file => file.name).some(file => file.name.toLowerCase().endsWith(dexState.f.input.base.toLowerCase()));
}

async function findCUEFile(dexState)
{
	const auxFiles = (dexState.f.files.aux || []).filter(auxFile => auxFile.ext.toLowerCase()===".cue");
	let validCUEFiles = await auxFiles.filterAsync(async auxFile => await validCUEFile(dexState, auxFile));
	if(validCUEFiles.length===0)
		validCUEFiles = auxFiles.filter(auxFile => auxFile.name.toLowerCase()===dexState.f.input.name.toLowerCase());
	return validCUEFiles[0];
}

export class iso extends Format
{
	name           = "CD Disc Image";
	website        = "http://fileformats.archiveteam.org/wiki/ISO_image";
	ext            = [".iso", ".bin", ".hfs", ".ugh", ".img", ".toast"];

	magic = [
		"ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", "CD-I disk image", "UDF disc image", "BIN with CUE", "ISO Archiv gefunden", "Format: ISO 9660", "PC-98 ISO",
		"ISO9660 file system", "UDF file system", "FM Towns bootable disk image", "Toast disk image", "BeOS BFS", "Xbox DVD file system", "deark: iso9660", "application/x-c2d",
		/^ISO 9660$/, /^UDF recognition sequence.*ISO9660/, /^fmt\/(468|1738)( |$)/,
		/^First .*are blank$/,
		..._RAW_MAGICS,
		...HFS_MAGICS, ...MFS_MAGICS
	];
	forbiddenMagic = [..._NULL_BYTES_MAGIC, ..._DMG_DISK_IMAGE_MAGIC];

	idMeta = ({macFileType, macFileCreator}) => (["GImg", "HImg", "hImg"].includes(macFileType) && macFileCreator==="CDr3") || (macFileType==="DOCI" && macFileCreator==="CDWr");

	idCheck = async (inputFile, detections, {extMatch, filenameMatch, idMetaMatch, fileSizeMatch, magicMatch, xlog}) =>
	{
		// this whole function is just to handle when we have an ext match to '.bin' or '.img' because they are so generic we need to check for other files. easier to do this than with a combination of 'auxFiles'
		const ext = inputFile.ext.toLowerCase();
		if(magicMatch || filenameMatch || idMetaMatch || fileSizeMatch || !extMatch || ![".bin", ".img"].includes(ext))
			return true;

		if(ext===".bin")
		{
			for(const cueFilePath of await fileUtil.tree(inputFile.dir, {depth : 1, nodir : true, regex : /\.cue$/i}))
			{
				const cueFiles = (await Program.runProgram("cueInfo", await DexFile.create(cueFilePath), {xlog : xlog.atLeast("debug") ? xlog : new XLog("none"), autoUnlink : true}))?.meta?.files || [];
				if(cueFiles.filter(file => file.name).some(file => file.name.toLowerCase().endsWith(inputFile.base.toLowerCase())))
					return true;
			}
		}
		else if(ext===".img")
		{
			for(const ccdFilePath of await fileUtil.tree(inputFile.dir, {depth : 1, nodir : true, regex : /\.ccd$/i}))
			{
				if(path.basename(ccdFilePath, path.extname(ccdFilePath)).toLowerCase()===inputFile.name.toLowerCase())
					return true;
			}
		}

		return false;
	};

	priority     = this.PRIORITY.HIGH;
	keepFilename = true;
	notes        = xu.trim`
	    This is a pretty big catch-all for many iso-like formats.
		Multiple CD formats are supported including: Photo CD, Video CD, Audio CD and CD-ROM (including HFS Mac filesystem support w/ resource forks).
		Multi-track (such as Audio and Data) are also supported.
		PC-ENGINE CD BIN/CUE files can't extract data, because there is no filesystem for PCE CDs as each CD's data tracks are different per game.
		NOTE: If the tracks are split across multiple .bin files, the 'first track' will merge with following non-audio tracks (which won't be processed, unless of type audio, those get processed alone)`;

	auxFiles = (input, otherFiles) =>
	{
		const otherExts = [".cue", ".toc", ".ccd"];
		let matches;

		// Priority #1: Files with the same name, but ending in a otherExts
		matches = otherFiles.filter(otherFile => otherExts.map(ext => input.name.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #2: Files with the same name including extension and ending in a otherExts
		matches = otherFiles.filter(otherFile => otherExts.map(ext => input.base.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #3: Files with the same name (further stripping of extension) and ending in a otherExts
		matches = otherFiles.filter(otherFile => otherExts.map(ext => path.basename(input.name, path.extname(input.name)).toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #4: Any files ending in .cue, as sometimes the .cue file isn't the same name as the .bin
		// We should probably also include .toc here, but we don't currently have a 'findTOCFile/validTOCFile' method, so we only include CUE files for now
		matches = otherFiles.filter(otherFile => otherFile.ext.toLowerCase()===".cue");
		if(matches.length>0)
			return matches;
		
		return false;
	};

	converters = async dexState =>
	{
		const fuseTree = dexState.meta?.fuseTree?.tree || [];
		delete dexState.meta?.fuseTree;

		const cueFile = await findCUEFile(dexState);
		let multiBinTracks = false;
		let multipleMode12Tracks = false;
		if(cueFile)
		{
			// Check to see if we are have tracks split across multiple .bin files
			const {meta : cueFileMeta} = await Program.runProgram("cueInfo", cueFile, {xlog : dexState.xlog || new XLog("none"), autoUnlink : true});
			if((cueFileMeta?.files || []).map(({name}) => name).unique().length>1)
			{
				if(cueFileMeta.files[0].name.toLowerCase().endsWith(dexState.f.input.base.toLowerCase()))
				{
					// first entry, combine all leading DATA tracks and re-try with dexvert and the combined file
					// NOTE: This currently only works if the file names in the CUE match exactly what is on disk
					dexState.xlog.debug`First data entry track of multi-bin file CUE/BIN. Concatenating all leading DATA tracks and passing along to dexvert as a converter.`;
					const dataTrackNames = [];
					for(const file of cueFileMeta.files)
					{
						if(file.tracks.some(track => track.type.toLowerCase()==="audio"))
							break;
						
						dataTrackNames.push(file.name);
					}

					dexState.xlog.debug`multiBinTracks detected: ${dataTrackNames.join(", ")}`;
					multiBinTracks = true;

					if(dataTrackNames.length>1)
						return [`cat[outputFilename:merged.iso][inputFilePaths:${base64Encode(JSON.stringify(dataTrackNames.map(dataTrackName => path.join(dexState.original.input.dir, dataTrackName))))}]`];

					// 1 or fewer non-audio tracks, just let it fall through and use the default converters
				}
				else if(cueFileMeta.files.filter(file => file.name).find(file => file.name.toLowerCase().endsWith(dexState.f.input.base.toLowerCase())).tracks.some(track => track.type.toLowerCase()==="audio"))
				{
					// Audio track, let it be handled normally
					dexState.xlog.debug`Audio track, let it be handled normally`;
				}
				else
				{
					// Some other track, ignore it
					dexState.xlog.debug`Some other track, should hopefully be included in track 1 conversion, but it's being ignored here.`;
					dexState.processed = true;
					return [];
				}
			}
			else
			{
				// Check to see if we have multiple MODE1 tracks
				multipleMode12Tracks = ((cueFileMeta?.files || [])?.[0]?.tracks || []).filter(o => ["MODE1/2352", "MODE2/2352"].includes(o.type)).length>1;
			}
		}

		const {meta : akailist} = await Program.runProgram("akailist", dexState.f.input, {xlog : dexState.xlog || new XLog("none"), autoUnlink : true});

		// If it's a VideoCD, prefer to rip it as video using 'vcdxrip'
		if(dexState.meta?.vcd?.isVCD && cueFile)
			return ["vcdxrip", "aaru", "IsoBuster", `bchunk[cueFilePath:${base64Encode(cueFile.absolute)}]`];
		else if(fuseTree.some(v => v.toLowerCase().startsWith("mpegav/avseq")))
			return ["vcdxrip[reRip]", "aaru"];

		// If it's a PhotoCD, rip using fuseiso (this is because regular mount doesn't work with bin/cue and bchunk produces tracks seperately which has images merged together and invalid dir structure for this format)
		if(dexState.meta?.photocd?.photocd)
			return ["fuseiso"];
		
		// We ASSUME that we'll never encounter a CD or disk that has a root level file/directory named: dexvert_nextstep, dexvert_mac, or dexvert_pc
		return [
			// We do a little trick here. We blindly try nextstep first. This won't produce output files if the ISO isn't in that format
			["uniso[nextstep]"].map(v => `${v}[subOutDir:dexvert_nextstep]`),

			// Next, if we don't have files yet, but detect as HFS, we first try extracting if hfs+ is identified. This is important because some CDs like MACPEOPLE-2001-06-01.ISO have both HFS and HFS+ but only HFS+ has good files
			() =>
			{
				const r = [];

				const firstHFSPlusPartition = (dexState.meta?.parted?.partitions || []).find(o => ["hfsx", "hfs+"].includes(o.filesystem));
				if(firstHFSPlusPartition)
					r.push(`hfsexplorer[partition:${firstHFSPlusPartition.number-1}][subOutDir:dexvert_mac]`);

				r.push("uniso[hfsplus][subOutDir:dexvert_mac]");	// otherwise things like cp115w.out don't get both mac and pc sides

				// No HFS+ was extracted, so we try to extract as HFS from our regular uniso which is preferred over hfsexplorer
				r.push("uniso[hfs][subOutDir:dexvert_mac]");

				// some mac ISOs have multiple partitions in them but only 1 partition is an HFS partition and to extract correctly I need to manually specify which one to hfsexplorer (MacAddict_068_2002_04.iso)
				const firstHFSPartition = (dexState.meta?.parted?.partitions || []).find(o => ["hfs"].includes(o.filesystem));
				if(firstHFSPartition)
					r.push(`hfsexplorer[partition:${firstHFSPartition.number-1}][subOutDir:dexvert_mac]`);
				r.push(`hfsexplorer[subOutDir:dexvert_mac]`);	// finally just try hfsexplorer and hope for the best

				// some ISO dumps are weird and don't work in anything other than IsoBuster and scummDumperCompanion (iso/Europe in the Round CD-ROM.iso)
				if(dexState.hasMagics("Apple Partition Map (APM) disk image") && dexState.hasMagics("Old-style Apple partition map"))
					r.push("scummDumperCompanion");	// Also possible here: "IsoBuster[subOutDir:dexvert_mac]"

				return r;
			},

			// finally we try all the others
			subState =>
			{
				const r = [];
				if(dexState.hasMagics(MFS_MAGICS))
					r.push("aaru");

				if(multipleMode12Tracks)		// Some CD's (Game_Killer.bin) have a ton of MODE1 tracks, not sure why, but the stuff below kinda chokes on them, but aaru/unar/fuseiso all seem to handle it ok, but we just pick aaru and fuseiso for now
					r.pushUnique("aaru", "fuseiso");
				r.push("uniso[checkMount]");	// Will only copy files if there are no input/output errors getting a directory listing (The PC-SIG Library on CD ROM - Ninth Edition.iso)

				// some multi-bin groups (sample/archive/iso/Oh!X 2001 Spring Special CD-ROM (Japan) (Track 1).bin) get messed up with bchunk, so if we have multiple bins, try fuseiso first
				if(multiBinTracks)
					r.pushUnique("fuseiso");

				// If we haven't't found any nextstep/hfs, then safe to try additional converters that may also handle those formats
				// If it's a BIN/CUE, run bchunk
				// This will include 'generated' cue files from .toc entries, thanks to the meta call below running first and it running toc2cue as needed
				// We try our regular uniso/fuseiso converters first though, because sometimes the cue file is pretty useless and using it can actually just cause problems
				if(!subState.f.files?.output?.length && cueFile)
					r.push(`bchunk[cueFilePath:${base64Encode(cueFile.absolute)}]`);

				r.push("uniso[block:512][checkMount]");		// Some isos have a 512 byte block size: McGraw-Hill Concise Encyclopedia of Science and Technology (852251-X)(1987).iso
				if(dexState.hasMagics(_RAW_MAGICS))
					r.push("ccd2iso");
				r.pushUnique("fuseiso");

				if(!subState.f.files?.output?.length)
				{
					if(dexState.original.input.ext.toLowerCase()===".iso")
						r.push("unar[matchType:magic]"); 	// Magazine Rack.iso can only being extracted with unar, weird

					r.pushUnique("aaru");
					r.push("deark[module:cd_raw] -> dexvert[skipVerify][bulkCopyOut]");

					// IsoBuster works here, but I prefer my own hfsutils implementation
					if(!dexState.hasMagics(HFS_MAGICS) && !dexState.hasMagics(_APPLE_DISK_COPY_MAGIC))
						r.push("IsoBuster[matchType:magic]");
				}

				r.push("cabextract[strongMatch]");	// Hobby PC 17.bin/cue has an audio track first, which bchunk does extract the ISO but only 'cabextract' can extract the ISO data, no idea why
				
				r.push("uniso", "uniso[block:512]");	// Fall back to uniso even with read/write errors

				if(dexState.hasMagics("null bytes"))	// Some isos have a lot of null bytes at the beginning which screws up other converters bu 7z seems to handle it (Cracking I..iso)
					r.push("sevenZip");

				// both of these can consume a lot of RAM and CPU, so best to only do it if there is a hint of being akai format
				if(akailist?.files?.length)
					r.push("akaiextract", "akairead");

				return r.map(v => `${v}[subOutDir:dexvert_pc]`);
			}
		];
	};

	meta = async (inputFile, dexState) =>
	{
		const xlog = dexState.xlog;
		const cueFile = await findCUEFile(dexState);
		const tocFile = (dexState.f.files.aux || []).find(auxFile => auxFile.base.toLowerCase().endsWith(".toc"));	// the auxFiles priority section above will ensure that only a filename matching .toc will be included

		// If we only have a TOC but no CUE, generate a CUE so we can bchunk it later
		// We do this conversion now because vcd-info requires the .cue file to be present to function
		if(!cueFile && tocFile)
		{
			dexState.tocCUEFilePath = path.join(tocFile.dir, `${tocFile.name}.cue`);
			const r = await Program.runProgram("toc2cue", tocFile, {outFile : dexState.tocCUEFilePath, xlog});
			await dexState.f.add("aux", r.f.outFile);
			await r.unlinkHomeOut();

			// Now we 'search' for it again, this ensures it's valid -- WHOOPS, uhm, this next line appears to do absolutely nothing
			await findCUEFile(dexState);
		}

		const meta = Object.fromEntries((await ["iso_info", "vcd_info", "photocd_info", "fuseTree", "parted", "lsdvd"].parallelMap(async programid =>
		{
			const infoR = await Program.runProgram(programid, inputFile, {xlog, autoUnlink : true});
			return [programid.split("_")[0], infoR.meta];
		}, 1)).filter(([, o]) => Object.keys(o).length>0));		// We restrict to 1 at a time (serial) so that the 'safe renaming' doesn't collide with each other

		Object.assign(dexState.meta, meta);
	};
	post = async dexState =>
	{
		// might produce up to 3 subdirectories. Delete any that are empty and if we have only 1 that has files then move those files up one level and delete the now empty subdirectory
		const types = await ["dexvert_nextstep", "dexvert_mac", "dexvert_pc"].parallelMap(async typeid =>
		{
			const r = {typeid, dirPath : path.join(dexState.f.outDir.absolute, typeid)};
			r.subPaths = await fileUtil.tree(r.dirPath, {depth : 1});
			return r;
		});

		const positiveTypes = types.filter(({subPaths}) => subPaths.length>0);
		for(const type of types)
		{
			if(type.subPaths.length===0)
				await fileUtil.unlink(type.dirPath);
			else if(positiveTypes.length>1)
				await Deno.rename(type.dirPath, path.join(path.dirname(type.dirPath), type.typeid.replaceAll("dexvert_", "")));
		}

		// if we have only one positive type, we need to move all files/folders in that dir up one level
		if(positiveTypes.length===1)
		{
			const type = positiveTypes[0];
			for(const subPath of type.subPaths)
				await Deno.rename(subPath, path.join(path.dirname(type.dirPath), path.basename(subPath)));
			await fileUtil.unlink(type.dirPath);

			if(dexState.meta?.fileMeta)
				dexState.meta.fileMeta = Object.fromEntries(Object.entries(dexState.meta.fileMeta).map(([k, v]) => [k.replace(new RegExp(`^${type.typeid}\\/`), ""), v]));
		}
		else
		{
			if(dexState.meta?.fileMeta)
				dexState.meta.fileMeta = Object.fromEntries(Object.entries(dexState.meta.fileMeta).map(([k, v]) => [k.replaceAll("dexvert_", ""), v]));
		}

		// Now check to see if we have both a 'mac' and a 'pc' directory, and if so delete any 'duplicate' files from the mac side to help save space
		const outputDirs = await fileUtil.tree(dexState.f.outDir.absolute, {depth : 1, nofile : true, relative : true});
		if(outputDirs.includes("mac") && outputDirs.includes("pc"))
		{
			const macRelPaths = await fileUtil.tree(path.join(dexState.f.outDir.absolute, "mac"), {nodir : true, relative : true});
			const pcRelPaths = await fileUtil.tree(path.join(dexState.f.outDir.absolute, "pc"), {nodir : true, relative : true});
			await pcRelPaths.parallelMap(async pcRelPath =>
			{
				const macRelPath = macRelPaths.find(v => v.toLowerCase()===pcRelPath.toLowerCase());
				if(!macRelPath)
					return;

				const macFilePath = path.join(dexState.f.outDir.absolute, "mac", macRelPath);
				const pcFilePath = path.join(dexState.f.outDir.absolute, "pc", pcRelPath);
				if(!await fileUtil.areEqual(macFilePath, pcFilePath))
					return;

				await fileUtil.unlink(macFilePath);
				await Deno.symlink(path.relative(path.dirname(macFilePath), pcFilePath), macFilePath);
			}, 2);
		}

		const videoTSDir = outputDirs.find(dir => dir.toLowerCase()==="video_ts");
		if(videoTSDir && dexState.meta?.lsdvd?.track?.length)
		{
			dexState.xlog.info`Found VIDEO_TS dir & lsdvd tracks. Converting with dvd2mp4.sh and replacing original VIDEO_TS directory...`;
			const tmpOutDirPath = await fileUtil.genTempPath(dexState.f.outDir.absolute);
			await Deno.mkdir(tmpOutDirPath);
			const videoTSDirPath = path.join(dexState.f.outDir.absolute, videoTSDir);
			await runUtil.run(Program.binPath("dvd2mp4.sh"), [dexState.f.input.absolute, tmpOutDirPath]);
			await fileUtil.unlink(videoTSDirPath, {recursive : true});
			await Deno.rename(tmpOutDirPath, videoTSDirPath);
		}
	};
}
