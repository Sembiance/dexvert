/*
import {Program} from "../../Program.js";

export class pco extends Program
{
	website = "https://vetusware.com/download/PC%20Outline%20for%20Windows%20PC%20Outline%201.0.a/?id=4597";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "https://vetusware.com/download/PC%20Outline%20for%20Windows%20PC%20Outline%201.0.a/?id=4597",
	unsafe  : true
};

exports.dos = () => "PCO/PCO.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.dosData = (state, p, r) => ({
	includeDir : true,
	timeout    : XU.MINUTE*3,
	autoExec   : [`COPY ${r.args[0].toUpperCase()} PCO\\F.PCO`, "CD PCO", "PCO.EXE"],
	keys       : [" ", " ", ["Down"], ["Return"], ["Return"], {delay : XU.SECOND*10}, ["Insert"], ["Right"], ["Right"], ["Right"], ["Right"], "d", "a", "g", "E:\\OUTFILE.TXT", ["Return"], ["Escape"], ["Escape"], "y"]
});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.cwd, "OUTFILE.TXT"), path.join(state.output.absolute, `${state.input.name}.txt`))(state, p, cb);
*/
