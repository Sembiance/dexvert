"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name     : "PowerPacker Archive",
	website : "http://fileformats.archiveteam.org/wiki/PowerPacker",
	ext      : [".pp"],
	magic    : [/^Power Packer.* compressed data/, "PowerPacker compressed"]
};

exports.steps = [() => ({program : "unar"})];

exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "in"), path.join(state.output.absolute, state.input.name))(state, p, cb);
