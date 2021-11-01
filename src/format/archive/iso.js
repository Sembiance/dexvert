"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	cueParser = require("cue-parser"),
	dexUtil = require("../../dexUtil.js"),
	C = require("../../C.js");

const HFS_MAGICS = ["Apple ISO9660/HFS hybrid CD image", /^Apple Driver Map.*Apple_HFS/, "PC formatted floppy with no filesystem"];

exports.meta =
{
	name          : "CD Disc Image",
	website       : "http://fileformats.archiveteam.org/wiki/ISO_image",
	ext           : [".iso", ".bin", ".hfs", ".ugh"],
	magic         : ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", ...HFS_MAGICS],
	priority      : C.PRIORITY.HIGH,
	keepFilename  : true,
	notes         : "Multiple CD formats are supported including: Photo CD, Video CD, Audio CD and CD-ROM (including HFS Mac filesystem support w/ resource forks). Multi-track (such as Audio and Data) are also supported.",
	filesOptional : (state, otherFiles) =>
	{
		const otherExts = [".cue", ".toc"];
		let matches = [];

		// Priority #1: Files with the same name, but ending in .cue or .toc
		matches = otherFiles.filter(otherFile => otherExts.map(ext => state.input.name.toLowerCase() + ext).includes(otherFile.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #2: Files with the same name including extension and ending in .cue or .toc
		matches = otherFiles.filter(otherFile => otherExts.map(ext => state.input.base.toLowerCase() + ext).includes(otherFile.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #3: Files with the same name (further stripping of extension) and ending in .cue or .toc
		matches = otherFiles.filter(otherFile => otherExts.map(ext => path.basename(state.input.name, path.extname(state.input.name)).toLowerCase() + ext).includes(otherFile.toLowerCase()));
		if(matches.length>0)
			return matches;

		// Priority #4: Any files ending in .cue or .toc, as sometimes the .cue/.toc file isn't the same name as the .bin
		matches = otherFiles.filter(otherFile => otherExts.map(ext => otherFile.toLowerCase().endsWith(ext)));
		if(matches.length>0)
			return matches;
		
		return matches;
	}
};

function validCUEFile(state, cueFilePath)
{
	let r=false;
	try
	{
		r = cueParser.parse(cueFilePath).files.filter(file => file.name).map(file => file.name.toLowerCase()).some(file => file.endsWith(state.input.base.toLowerCase()));
	}
	catch(err)
	{
		if(state.verbose>=4)
			XU.log`HANDLED. Invalid CUE file ${cueFilePath} with error: ${err}`;
	}

	return r;
}

function findCUEFile(state)
{
	return (state.extraFilenames || []).find(v => v.toLowerCase().endsWith(".cue") && validCUEFile(state, path.join(state.cwd, v)));
}

exports.steps =
[
	(state, p) =>
	{
		const cueFilePath = findCUEFile(state);

		// If it's a VideoCD, rip video using 'vcdxrip' and files with 'bchunk'
		if(state.input.meta?.vcd?.isVCD && cueFilePath)
		{
			return p.util.flow.serial([
				() => ({program : "vcdxrip"}),
				() => p.util.file.findValidOutputFiles(),
				() =>
				{
					// If vcdxrip failed to produce a avseq01.mpg file, then we fall back to IsoBuster
					if(!state.output.files.includes("avseq01.mpg"))
						return ({program : "IsoBuster"});

					// Otherwise we run bchunk to get the 'regular' files
					return ({program : "bchunk", argsd : [undefined, undefined, path.join(state.cwd, cueFilePath)]});
				}
			]);
		}
		
		// If it's a PhotoCD, rip using fuseiso (this is because regular mount doesn't work with bin/cue and bchunk produces tracks seperately which has images merged together and invalid dir structure for this format)
		if(state.input.meta?.photocd?.photocd)
			return ({program : "fuseiso"});
		
		// If it's a BIN/CUE, run bchunk
		if(cueFilePath)
			return ({program : "bchunk", argsd : [undefined, undefined, path.join(state.cwd, cueFilePath)]});

		// If it was a BIN/TOC, run bchunk with the converted CUE file
		if(state.tocCUEFilePath)
		{
			const tmpCUEFilePath = state.tocCUEFilePath;
			delete state.tocCUEFilePath;
			return ({program : "bchunk", argsd : [undefined, undefined, tmpCUEFilePath]});
		}

		// Finally, we just use uniso
		const r = {program : "uniso"};
		
		// CDs can be hybrid Mac/PC CDs, thus have both HFS and non-HFS tracks
		// HFS is problematic though, so we prefer to extract the PC/ISO version if available
		// So we only set the uniso 'hfs' flag if we have an HFS track and we do NOT detect a regular ISO-9660 track (by checking if iso-info)
		const isHFS = state.identify.some(identification => HFS_MAGICS.some(matchAgainst => dexUtil.flexMatch(identification.magic, matchAgainst)));
		if(isHFS)
		{
			// Sometimes though the PC side is just 'empty' or blank (Odyssey Legend of Nemesis) so we will have to re-try later with HFS uniso if we don't get any files out
			if(state.input.meta?.iso?.isISO)
				state.fallbackToHFSUniso = true;
			else
				r.flags = {hfs : true};
		}

		return r;
	},
	() => ({program : "fixPerms"}),
	(state, p) => ((state.output.files || []).length>0 ? p.util.flow.noop : p.util.file.findValidOutputFiles()),
	(state, p) =>
	{
		// If we don't have HFS ISO to fall back to, or we have output files, then we are done
		if(!state.fallbackToHFSUniso || (state.output.files || []).length>0)
			return p.util.flow.noop;

		return ({program : "uniso", flags : {hfs : true}});
	},

	// Some ISOs fail above but seem to work with fuseiso, so fall back to that
	(state, p) => ((state.output.files || []).length>0 ? p.util.flow.noop : p.util.file.findValidOutputFiles()),
	(state, p) => ((state.output.files || []).length>0 ? p.util.flow.noop : {program : "fuseiso"}),
	() => ({program : "fixPerms"})
];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) =>
	{
		const cueFilePath = findCUEFile(state);
		const tocFilePath = (state.extraFilenames || []).find(extraFilename => extraFilename.toLowerCase().endsWith(".toc"));

		// If we only have a TOC but no CUE, generate a CUE so we can bchunk it later
		// We do this conversion now because vcd-info requires the .cue file to be present to function
		if(!cueFilePath && tocFilePath)
		{
			state.tocCUEFilePath = path.join(state.cwd, `${path.basename(tocFilePath, path.extname(tocFilePath))}.cue`);
			return ({program : "toc2cue", argsd : [tocFilePath, state.tocCUEFilePath]});
		}
		
		return p.util.flow.noop;
	},
	(state, p) =>
	{
		const cueFilePath = findCUEFile(state);
		if(!cueFilePath && state.tocCUEFilePath)
		{
			if(!validCUEFile(state, state.tocCUEFilePath))
			{
				delete state.tocCUEFilePath;
			}
			else
			{
				// We have to add it to extraFilenames because this is how 'findCUEFile' works, which is needed later on
				if(!state.extraFilenames)
					state.extraFilenames = [];
				state.extraFilenames.push(path.basename(state.tocCUEFilePath));
			}
		}

		return p.util.flow.noop;
	},
	() => ({program : "iso-info"}),
	() => ({program : "vcd-info"}),
	() => ({program : "photocd-info"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "iso-info"))
			state.input.meta.iso = p.util.program.getMeta(state, "iso-info");
		if(p.util.program.getMeta(state, "vcd-info"))
			state.input.meta.vcd = p.util.program.getMeta(state, "vcd-info");
		if(p.util.program.getMeta(state, "photocd-info"))
			state.input.meta.photocd = p.util.program.getMeta(state, "photocd-info");

		return p.util.flow.noop;
	}
])(state0, p0, cb);
