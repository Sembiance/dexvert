/*
import {Program} from "../../Program.js";

export class fc-scan extends Program
{
	website = "https://fontconfig.org";
	gentooPackage = "media-libs/fontconfig";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website        : "https://fontconfig.org",
	gentooPackage  : "media-libs/fontconfig",
	informational  : true
};

exports.bin = () => "fc-scan";

// Valid properties: https://www.freedesktop.org/software/fontconfig/fontconfig-user.html#AEN21

const STRINGS = ["family", "familyLang", "style", "styleLang", "fullName", "fullNameLang", "foundry", "rasterizer", "lang", "capability", "fontFormat", "fontFeatures", "nameLang", "prgName", "postscriptName", "charset"];
const NUMS = ["size", "aspect", "pixelSize", "index", "scale", "dpi", "fontVersion"];
const BOOLS = ["antialias", "hinting", "verticalLayout", "autoHint", "globalAdvance", "outline", "scalable", "color", "minspace", "embolden", "embeddedBitmap", "decorative"];
const LOOKUPS =
{
	"slant"     : {0 : "roman", 100 : "italic", 110 : "oblique"},
	"weight"    : {0 : "thin", 40 : "extralight", 50 : "light", 55 : "semilight", 75 : "book", 80 : "normal", 100 : "medium", 180 : "semibold", 200 : "bold", 205 : "extrabold", 210 : "heavy"},
	"width"     : {50 : "ultracondensed", 63 : "extracondensed", 75 : "condensed", 87 : "semicondensed", 100 : "normal", 113 : "semicondensed", 125 : "expanded", 150 : "extraexpanded", 200 : "ultraexpanded"},
	"spacing"   : {0 : "proportional", 90 : "dual", 100 : "mono", 110 : "charcell"},
	"hintStyle" : {0 : "none", 1 : "slight", 2 : "medium", 3 : "full"},
	"rgba"      : {0 : "unknown", 1 : "rgb", 2 : "bgr", 3 : "vrgb", 4 : "vbgr", 5 : "none"},
	"lcdFilter" : {0 : "none", 1 : "default", 2 : "light", 3 : "legacy"}
};

const PROPS = [...STRINGS, ...NUMS, ...BOOLS, ...Object.keys(LOOKUPS)];
exports.args = (state, p, r, inPath=state.input.filePath) => (["--format", PROPS.map(PROP => `${PROP}:%{${PROP.toLowerCase()}}`).join("\n"), inPath]);
exports.post = (state, p, r, cb) =>
{
	const meta = {};
	(r.results || "").split("\n").forEach(line =>
	{
		const [key, ...valueRaw] = line.split(":");
		if(!PROPS.includes(key))
			return;

		const value = valueRaw.join("").trim();
		if(value.length===0 || value.startsWith(`%{${key.toLowerCase()}}`))
			return;

		meta[key] = NUMS.includes(key) ? +value : (BOOLS.includes(key) ? value==="True" : value);
		if(LOOKUPS[key])
			meta[key] = LOOKUPS[key][meta[key]] || meta[key];
		if(key==="lang")
			meta[key] = meta[key].split("|");
		
		if(meta[key]==="unknown")
			delete meta[key];
	});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
*/
