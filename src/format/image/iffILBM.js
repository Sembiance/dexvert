"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	image = require("../../family/image.js"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

exports.meta =
{
	name     : "IFF Interleaved Bitmap Image",
	website  : "http://fileformats.archiveteam.org/wiki/ILBM",
	ext      : [".lbm", ".ilbm", ".iff", ".beam", ".dhr", ".dr", ".mp", ".dctv"],
	mimeType : "image/x-ilbm",
	magic    : ["IFF InterLeaved BitMap", "IFF data, ILBM interleaved image", "Interchange File Format Interleaved Bitmap", "IFF ILBM bitmap", "DCTV encoded ILBM bitmap"],
	notes    : XU.trim`
		Some ILBM files were only used to hold a palette and nothing more. This won't convert those.
		Others have EMPTY (zeros) CMAP palettes which confuse the converter programs. So I detect this and remove the CMAP entry which allows the converters to fallback to a default converter.
		DPPS chunk - Present in some files and they don't convert correctly. Probably a 'Deluxe Paint' chunk of some sort.
		CRNG chunk - Used for color shifting. Abydos supports some of these (used by Deluxe Paint)`
};

exports.preSteps =
[
	() => (state, p, cb) =>
	{
		tiptoe(
			function loadFileData()
			{
				fs.readFile(state.input.absolute, this);
			},
			function checkForNullCMAPPalette(inputBuffer)
			{
				// Some IFF files have a CMAP entries, but it's filled with all zeroes. Here we DELETE the CMAP entry if that's the case, so that the converter programs fall back on a 'default' palette of colors
				const cmapLoc = inputBuffer.indexOf("CMAP");
				if(cmapLoc===-1)
					return this();
				
				const cmapSize = inputBuffer.readUInt32BE(cmapLoc+4);
				if(Buffer.compare(inputBuffer.slice(cmapLoc+8, cmapLoc+8+cmapSize), Buffer.alloc(cmapSize, 0))===0)
				{
					state.input.filePath = fileUtil.generateTempFilePath("", ".ilbm");
					return fs.writeFile(state.input.filePath, Buffer.concat([inputBuffer.slice(0, cmapLoc), inputBuffer.slice(cmapLoc+8+cmapSize)]), this);
				}
				
				this();
			},
			cb
		);
	}
];

exports.converterPriority = ["recoil2png", "deark", {program : "ffmpeg", flags : {ffmpegFormat : "iff"}}, "convert"];

exports.steps =
[
	// abydosconvert handles IFF files the best (BY FAR), including color cycling animations in WEBP format (AH_Dan, AH_Eye, Watch, DECKER-BattleMech)
	// But it sometimes produces crazy fast color cycles and they can sometimes be so rapid that the original meaning of the image is lost
	// It also as of v0.2.3 doesn't handle certain images correctly such as GINA and foto57
	// So we first do abydosconvert and then try the other programs. abydos will produce a .webp for it's animated output which the other programs don't produce
	() => ({program : "abydosconvert"}),
	(state, p) => p.util.file.findValidOutputFiles(),
	(state, p) => p.family.validateOutputFiles,
	...image.converterSteps
];
