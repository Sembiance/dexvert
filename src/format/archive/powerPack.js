/*
import {Format} from "../../Format.js";

export class powerPack extends Format
{
	name = "PowerPacker Archive";
	website = "http://fileformats.archiveteam.org/wiki/PowerPacker";
	ext = [".pp"];
	magic = [{},"PowerPacker compressed"];
	notes = "Some files (Image & Aonia) won't extract (tried unar, ancient, ppunpack). I could install PowerPacker on the QEMU amiga and decrunch there. I looked at v4.0 and it was a nightmare to install, so I punted.";
	converters = ["unar"]

post = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	name    : "PowerPacker Archive",
	website : "http://fileformats.archiveteam.org/wiki/PowerPacker",
	ext     : [".pp"],
	magic   : [/^Power Packer.* compressed data/, "PowerPacker compressed"],
	notes   : "Some files (Image & Aonia) won't extract (tried unar, ancient, ppunpack). I could install PowerPacker on the QEMU amiga and decrunch there. I looked at v4.0 and it was a nightmare to install, so I punted."
};

exports.converterPriority = ["unar"];

exports.post = (state, p, cb) => p.util.file.move(path.join(state.output.absolute, "in"), path.join(state.output.absolute, state.input.name))(state, p, cb);

*/
