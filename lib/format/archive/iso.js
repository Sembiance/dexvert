"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require("../../C.js");

exports.HFS_MAGICS = ["Apple ISO9660/HFS hybrid CD image", /^Apple Driver Map.*Apple_HFS/];

exports.meta =
{
	name          : "CD Disc Image",
	website       : "http://fileformats.archiveteam.org/wiki/ISO_image",
	ext           : [".iso", ".bin", ".hfs", ".ugh"],
	magic         : ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", ...exports.HFS_MAGICS],
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

exports.steps =
[
	(state, p) =>
	{
		const cueFilePath = (state.extraFilenames || []).find(extraFilename => extraFilename.toLowerCase().endsWith(".cue"));
		const tocFilePath = (state.extraFilenames || []).find(extraFilename => extraFilename.toLowerCase().endsWith(".toc"));
		// If we only have a TOC but no CUE, generate a CUE so we can bchunk it later
		if(!cueFilePath && tocFilePath)
		{
			state.tocCUEFilePath = path.join(state.cwd, `${path.basename(tocFilePath, path.extname(tocFilePath))}.cue`);
			return ({program : "toc2cue", argsd : [tocFilePath, state.tocCUEFilePath]});
		}
		
		return p.util.flow.noop;
	},
	(state, p) =>
	{
		const cueFilePath = (state.extraFilenames || []).find(extraFilename => extraFilename.toLowerCase().endsWith(".cue"));

		// If it's a VideoCD, rip video using 'vcdxrip' and files with 'bchunk'
		if(state.input.meta?.vcd?.isVCD && cueFilePath)
			return p.util.flow.serial([() => ({program : "vcdxrip"}), () => ({program : "bchunk", argsd : [undefined, undefined, path.join(state.cwd, cueFilePath)]})]);
		
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

		// Otherwise we use uniso
		return ({program : "uniso"});
	},
	() => ({program : "fixPerms"})
];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
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
