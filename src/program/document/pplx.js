/*
import {Program} from "../../Program.js";

export class pplx extends Program
{
	website = "http://files.mpoli.fi/unpacked/tlr/pcboard_bbs_utilities/agsppx20.zip/";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://files.mpoli.fi/unpacked/tlr/pcboard_bbs_utilities/agsppx20.zip/"
};

exports.dos = () => "PPLX.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.dosData = (state, p, r) => ({timeout : XU.MINUTE, autoExec : [`PPLX.EXE ${r.args[0]}`, `COPY ${path.basename(r.args[0], path.extname(r.args[0]))}.PPX OUT`]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "IN.PPX"), path.join(state.output.absolute, `${state.input.name}.ppx`))(state, p, cb);
*/
