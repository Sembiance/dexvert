"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
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

// abydosconvert handles IFF files the best, including color cycling animations in WEBP format (AH_Dan, AH_Eye, Watch). It does have issues with foto57 as of v0.2.3
// recoil2png converts IFF files second best, getting all test files correct
// nconvert and convert both mess up these: beautyfc, breakfst, hameset*, pchgcmp, agony
exports.converterPriorty = ["abydosconvert", "recoil2png", "convert", "nconvert"];
