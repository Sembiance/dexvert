"use strict";
const XU = require("@sembiance/xu"),
	C = require("../../C.js");

exports.meta =
{
	name          : "ISO Disc Image",
	website       : "http://fileformats.archiveteam.org/wiki/ISO_image",
	ext           : [".iso", ".bin"],
	magic         : ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", "Apple ISO9660/HFS hybrid CD image"],
	priority      : C.PRIORITY.HIGH, // ISO should be done before almost everything else (except for other CDROM formats like Nero)
	keepFilename  : true,
	filesRequired : (state, otherFiles) =>
	{
		const ourExt = state.input.ext.toLowerCase();
		// .bin files require a corresponding .cue
		if(ourExt===".bin")
			return otherFiles.filter(otherFile => otherFile.toLowerCase()===`${state.input.name.toLowerCase()}.cue`);

		return false;
	},
	notes : "Multiple CD formats are supported including: Photo CD, Video CD, Audio CD and CD-ROM (including HFS Mac filesystem support w/ resource forks). Multi-track (such as Audio and Data) are also supported."
};

exports.converterPriorty = ["uniso"];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "iso-info"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "iso-info"))
			state.input.meta.iso = p.util.program.getMeta(state, "iso-info");

		return p.util.flow.noop;
	}
])(state0, p0, cb);
