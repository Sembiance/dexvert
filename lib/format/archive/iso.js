"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

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
	}
};

exports.steps = [() => ({program : "uniso"})];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "iso-info"}),
	(state, p) =>
	{
		if(state.run.meta["iso-info"])
		{
			state.input.meta.iso = state.run.meta["iso-info"];
			delete state.run.meta["iso-info"];
		}


		return p.util.flow.noop;
	}
])(state0, p0, cb);
