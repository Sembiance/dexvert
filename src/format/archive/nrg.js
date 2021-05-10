"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	StreamSkip = require("stream-skip"),
	path = require("path"),
	C = require("../../C.js");

exports.meta =
{
	name    : "Nero CD Image",
	website : "http://fileformats.archiveteam.org/wiki/NRG",
	ext     : [".nrg"],
	magic   : ["Nero CD image"],
	priority : C.PRIORITY.TOP	// NRG is often mis-identified as ISO
};

exports.steps =
[
	() => (state, p, cb) =>
	{
		// According to nrg2iso we just skip the first 307,200 bytes: http://gregory.kokanosky.free.fr/v4/linux/nrg2iso.en.html
		const inStream = fs.createReadStream(state.input.absolute);
		inStream.on("error", cb);
		inStream.on("end", cb);
		inStream.pipe(new StreamSkip({skip : 307200})).pipe(fs.createWriteStream(path.join(state.cwd, "in.iso")));
	},
	state => ({program : "uniso", argsd : [path.join(state.cwd, "in.iso")]}),
	() => ({program : "fixPerms"})
];
