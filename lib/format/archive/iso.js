"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	C = require(path.join(__dirname, "..", "..", "C.js"));

exports.meta =
{
	name     : "ISO Disc Image",
	website  : "http://fileformats.archiveteam.org/wiki/ISO_image",
	ext      : [".iso"],
	magic    : ["ISO 9660 CD image", "ISO 9660 CD-ROM filesystem data", "ISO Disk Image File", "Apple ISO9660/HFS hybrid CD image"],
	priority : C.PRIORITY.HIGH	// ISO should be done before almost everything else (except for other CDROM formats like Nero)
};

exports.steps = [() => ({program : "uniso"})];

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	() => ({program : "iso-info"}),
	(state, p) =>
	{
		if(state.run["iso-info"] && state.run["iso-info"].length>0 && state.run["iso-info"][0])
		{
			const meta = {};
			state.run["iso-info"][0].trim().split("\n").forEach(line =>
			{
				const {key, val} = (line.trim().match(/^(?<key>[^:]+)\s*:\s*(?<val>.+)$/) || {groups : {}}).groups;
				if(key && val && !["ISO 9660 image", "iso-info", "++ WARN"].some(v => key.trim().startsWith(v)))
					meta[key.trim().toCamelCase()] = val.trim();
			});
			if(Object.keys(meta).length>0)
				state.input.meta.iso = meta;
		}

		return p.util.flow.noop;
	}
])(state0, p0, cb);
