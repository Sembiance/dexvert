/*
import {Program} from "../../Program.js";

export class draw256 extends Program
{
	website = "http://cd.textfiles.com/megarom/megarom3/GRAPHICS/APPS/DRAWV221.ZIP";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://cd.textfiles.com/megarom/megarom3/GRAPHICS/APPS/DRAWV221.ZIP",
	unsafe  : true
};

exports.dos = () => "DRAW256/DRAW256.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([`..\\${inPath}`]);
exports.dosData = (state, p, r) => ({includeDir : true, autoExec : ["CD DRAW256", `DRAW256.EXE ${r.args}`], keys : ["s", "..\\F.PCX", ["Return"], ["Escape"], "y"]});
exports.post = (state, p, r, cb) => p.util.program.run("convert", {argsd : ["F.PCX"]})(state, p, cb);
*/
