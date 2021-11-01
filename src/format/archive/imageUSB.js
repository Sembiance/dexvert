"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs"),
	tiptoe = require("tiptoe"),
	StreamSkip = require("stream-skip"),
	path = require("path");

exports.meta =
{
	name    : "imageUSB",
	website : "https://forums.passmark.com/other-software/5213-opening-imageusb-bin-output-file-with-different-software",
	ext     : [".usbimage"],
	magic   : ["imageUSB"]
};

// Must be greater than 512 bytes in length, since that's how long the imageUSB header is
exports.idCheck = state => fs.statSync(state.input.absolute).size>512;

exports.steps =
[
	() => (state, p, cb) =>
	{
		tiptoe(
			function pipeFileWithoutHeader()
			{
				const inStream = fs.createReadStream(state.input.absolute);
				inStream.on("error", this);
				inStream.on("end", this);
				inStream.pipe(new StreamSkip({skip : 512})).pipe(fs.createWriteStream(path.join(state.output.absolute, state.input.name)));
			},
			cb
		);
	}
];
