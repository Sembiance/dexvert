/*
import {Program} from "../../Program.js";

export class dexmagic extends Program
{
	website = "https://github.com/Sembiance/dexmagic";
	informational = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexmagic",
	informational : true
};

const STARTS_WITH_CHECKS =
{
	"CAD/Draw TVG"             : "TommySoftware TVG",
	"Second Nature Slide Show" : "Second Nature Software\r\nSlide Show\r\nCollection"
};
Object.mapInPlace(STARTS_WITH_CHECKS, (k, v) => (v instanceof Buffer ? v : Buffer.from(v)));

exports.bin = () => "dexmagic";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function openFile()
		{
			fs.open(r.args[0], this);
		},
		function loadFile(fd)
		{
			this.data.fd = fd;

			const maxCompareSize = Object.values(STARTS_WITH_CHECKS).map(v => v.length).max();
			this.data.fileData = Buffer.alloc(maxCompareSize);

			fs.read(this.data.fd, this.data.fileData, 0, maxCompareSize, 0, this);
		},
		function performChecks()
		{
			r.results = [...r.results.trim().split("\n"), ...Object.keys(STARTS_WITH_CHECKS).filter(checkName => this.data.fileData.subarray(0, STARTS_WITH_CHECKS[checkName].length).equals(STARTS_WITH_CHECKS[checkName]))].join("\n");

			fs.close(this.data.fd, this);
		},
		cb
	);
};
*/
