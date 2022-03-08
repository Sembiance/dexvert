import {xu} from "xu";
import {Format} from "../../Format.js";
import {Program} from "../../Program.js";
import {path, base64Encode} from "std";

const HFS_MAGICS = ["Apple ISO9660/HFS hybrid CD image", /^Apple Driver Map.*Apple_HFS/, "PC formatted floppy with no filesystem"];

async function validCUEFile(dexState, cueFile)
{
	const cueInfoR = await Program.runProgram("cueInfo", cueFile, {xlog : dexState.xlog, autoUnlink : true});
	return (cueInfoR.meta?.files || []).filter(file => file.name).some(file => file.name.toLowerCase().endsWith(dexState.f.input.base.toLowerCase()));
}

async function findCUEFile(dexState)
{
	const auxFiles = (dexState.f.files.aux || []).filter(auxFile => auxFile.ext.toLowerCase()===".cue");
	const validCUEFiles = await auxFiles.filterAsync(async auxFile => await validCUEFile(dexState, auxFile));
	return validCUEFiles[0];
}

export class iso extends Format
{
	name         = "CD Disc Image";
	website      = "http://fileformats.archiveteam.org/wiki/ISO_image";
	ext          = [".iso", ".bin", ".hfs", ".ugh"];
	magic        = ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", ...HFS_MAGICS];
	priority     = this.PRIORITY.HIGH;
	keepFilename = true;
	notes        = xu.trim`
		Multiple CD formats are supported including: Photo CD, Video CD, Audio CD and CD-ROM (including HFS Mac filesystem support w/ resource forks).
		Multi-track (such as Audio and Data) are also supported.
		PC-ENGINE CD BIN/CUE files can't extract data, because there is no filesystem for PCE CDs, etach CD's data tracks are different per game.
		NOTE: If the tracks are split across multiple .bin files, this is NOT currently supported.`;
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

		// If it's a VideoCD, rip video using 'vcdxrip' and files with 'bchunk'
		if(dexState.meta?.vcd?.isVCD && cueFile)
			return ["vcdxrip", "IsoBuster", `bchunk[cueFilePath:${base64Encode(cueFile.absolute)}]`];

		// If it's a PhotoCD, rip using fuseiso (this is because regular mount doesn't work with bin/cue and bchunk produces tracks seperately which has images merged together and invalid dir structure for this format)
		if(dexState.meta?.photocd?.photocd)
			return ["fuseiso"];

		// CDs can be Mac HFS CDs, or even hybrid Mac/PC CDs that have both HFS and non-HFS tracks
		// HFS isn't as ideal to extract due to all the resource forked files, so we prefer to extract the PC/ISO version if available
		// So we only set the uniso 'hfs' flag if we have an HFS track and we do NOT detect a regular ISO-9660 track (which was checked with iso-info in meta call)
		const {flexMatch} = await import("../../identify.js");	// need to import this dynamically to avoid circular dependency
		const isHFS = dexState.ids.some(id => HFS_MAGICS.some(matchAgainst => flexMatch(id.magic, matchAgainst)));
		
		// Sometimes the PC side is present, but is empty/blank (Odyssey Legend of Nemesis) so if we detect isISO, we try PC side first, but fall back to HFS side to be safe
		// If isISO isn't set at all (Mac User Ultimate Mac Companion 1996.bin) then we just extract the hfs side
		const hfsConverters = [...(dexState.meta?.iso?.isISO ? ["uniso", "uniso[hfs]"] : ["uniso[hfs]"]), "fuseiso"];

		// If it's a BIN/CUE, run bchunk
		// This will include 'generated' cue files from .toc entries, thanks to the meta call below running first and it running toc2cue as needed
		// We try our regular converters first though, because sometimes the cue file is pretty useless
		if(cueFile)
			return [...(isHFS ? hfsConverters : ["uniso"]), `bchunk[cueFilePath:${base64Encode(cueFile.absolute)}]`, "fuseiso"];

		if(isHFS)
			return hfsConverters;
		
		// Finally, we appear to have just a 'simple' iso file. So just use uniso and fallback on fuseiso
		return ["uniso", "fuseiso"];
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
		})).filter(([, o]) => Object.keys(o).length>0));

		Object.assign(dexState.meta, meta);
	};
}
