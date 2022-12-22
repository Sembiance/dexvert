import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";
import {Program} from "../../Program.js";
import {path, base64Encode} from "std";
import {XLog} from "xlog";
import {_DMG_DISK_IMAGE_MAGIC} from "./dmg.js";
import {_MACBINARY_MAGIC} from "./macBinary.js";
import {_NULL_BYTES_MAGIC} from "../other/nullBytes.js";

const HFS_MAGICS = ["Apple ISO9660/HFS hybrid CD image", /^Apple Driver Map.*Apple_HFS/, "PC formatted floppy with no filesystem", "High Sierra CD-ROM"];

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
	forbidExtMatch = [".img"];

	magic          = ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", /^fmt\/468( |$)/, ...HFS_MAGICS, ..._MACBINARY_MAGIC];
	weakMagic      = _MACBINARY_MAGIC;
	forbiddenMagic = [..._NULL_BYTES_MAGIC, ..._DMG_DISK_IMAGE_MAGIC];

	priority     = this.PRIORITY.HIGH;
	keepFilename = true;
	notes        = xu.trim`
		Multiple CD formats are supported including: Photo CD, Video CD, Audio CD and CD-ROM (including HFS Mac filesystem support w/ resource forks).
		Multi-track (such as Audio and Data) are also supported.
		PC-ENGINE CD BIN/CUE files can't extract data, because there is no filesystem for PCE CDs, etach CD's data tracks are different per game.
		NOTE: If the tracks are split across multiple .bin files, the 'first track' will merge with following non-audio tracks (which won't be processed, unless of type audio, those get processed alone)`;

	auxFiles     = (input, otherFiles) =>
	{
		const otherExts = [".cue", ".toc"];
		let matches = [];

		// Priority #1: Files with the same name, but ending in .cue or .toc
		matches = otherFiles.filter(otherFile => otherExts.map(ext => input.name.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #2: Files with the same name including extension and ending in .cue or .toc
		matches = otherFiles.filter(otherFile => otherExts.map(ext => input.base.toLowerCase() + ext).includes(otherFile.base.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #3: Files with the same name (further stripping of extension) and ending in .cue or .toc
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
		const cueFile = await findCUEFile(dexState);
		if(cueFile)
		{
			// Check to see if we are have tracks split across multiple .bin files
			const {meta : cueFileMeta} = await Program.runProgram("cueInfo", cueFile, {xlog : dexState.xlog, autoUnlink : true});
			if(cueFileMeta.files.map(({name}) => name).unique().length>1)
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
		}

		// If it's a VideoCD, rip video using 'vcdxrip' and files with 'bchunk'
		if(dexState.meta?.vcd?.isVCD && cueFile)
			return ["vcdxrip", "IsoBuster", `bchunk[cueFilePath:${base64Encode(cueFile.absolute)}]`];

		// If it's a PhotoCD, rip using fuseiso (this is because regular mount doesn't work with bin/cue and bchunk produces tracks seperately which has images merged together and invalid dir structure for this format)
		if(dexState.meta?.photocd?.photocd)
			return ["fuseiso"];
		
		// We ASSUME that we'll never encounter a CD or disk that has a root level file/directory named: dexvert_nextstep, dexvert_mac, or dexvert_pc
		return [
			// We do a little trick here. We blindly try nextstep and hfsplus/hfs. These won't produce output files if the ISO isn't in that format
			["uniso[nextstep]"].map(v => `${v}[subOutDir:dexvert_nextstep]`),
			["uniso[hfsplus]", "uniso[hfs]"].map(v => `${v}[subOutDir:dexvert_mac]`),

			subState =>
			{
				const r = [
					"uniso[checkMount]"		// Will only copy files if there are no input/output errors getting a directory listing (The PC-SIG Library on CD ROM - Ninth Edition.iso)
				];

				// If we haven't't found any nextstep/hfsplus/hfs, then safe to try additional converters that may also handle those formats
				// If it's a BIN/CUE, run bchunk
				// This will include 'generated' cue files from .toc entries, thanks to the meta call below running first and it running toc2cue as needed
				// We try our regular uniso/fuseiso converters first though, because sometimes the cue file is pretty useless and using it can actually just cause problems
				if(!subState.f.files?.output?.length && cueFile)
					r.push(`bchunk[cueFilePath:${base64Encode(cueFile.absolute)}]`);

				r.push(
					"uniso[block:512][checkMount]",	// Some isos have a 512 byte block size: McGraw-Hill Concise Encyclopedia of Science and Technology (852251-X)(1987).iso
					"fuseiso"
				);

				if(!subState.f.files?.output?.length)
				{
					if(dexState.original.input.ext.toLowerCase()===".iso")
						r.push("unar[matchType:magic]"); 	// Magazine Rack.iso can only being extracted with unar, weird

					r.push(
						"deark[module:cd_raw] -> dexvert[skipVerify][bulkCopyOut]",
						"IsoBuster[matchType:magic]"
					);
				}

				r.push("cabextract[matchType:magic]");	// Hobby PC 17.bin/cue has an audio track first, which bchunk does extract the ISO but only 'cabextract' can extract the ISO data, no idea why
				
				r.push("uniso", "uniso[block:512]");	// Fall back to uniso even with read/write errors

				return r.map(v => `${v}[subOutDir:dexvert_pc]`);
			}
		];
	};

	meta = async (inputFile, dexState) =>
	{
		const xlog = dexState.xlog;
		let cueFile = await findCUEFile(dexState);
		const tocFile = (dexState.f.files.aux || []).find(auxFile => auxFile.base.toLowerCase().endsWith(".toc"));	// the auxFiles priority section above will ensure that only a filename matching .toc will be included

		// If we only have a TOC but no CUE, generate a CUE so we can bchunk it later
		// We do this conversion now because vcd-info requires the .cue file to be present to function
		if(!cueFile && tocFile)
		{
			dexState.tocCUEFilePath = path.join(tocFile.dir, `${tocFile.name}.cue`);
			const r = await Program.runProgram("toc2cue", tocFile, {outFile : dexState.tocCUEFilePath, xlog});
			await dexState.f.add("aux", r.f.outFile);
			await r.unlinkHomeOut();

			// Now we 'search' for it again, this ensures it's valid
			cueFile = await findCUEFile(dexState);
		}

		const meta = Object.fromEntries((await ["iso_info", "vcd_info", "photocd_info"].parallelMap(async programid =>
		{
			const infoR = await Program.runProgram(programid, inputFile, {xlog, autoUnlink : true});
			return [programid.split("_")[0], infoR.meta];
		}, 1)).filter(([, o]) => Object.keys(o).length>0));		// We restrict to 1 at a time (serial) so that the 'safe renaming' doesn't collide with each other

		Object.assign(dexState.meta, meta);
	};
	post = async dexState =>
	{
		Object.assign(dexState.meta, dexState.ran.find(({programid, meta}) => programid==="uniso" && meta?.fileMeta)?.meta || {});

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
		}
	};
}
