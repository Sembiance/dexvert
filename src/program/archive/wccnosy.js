/*
import {Program} from "../../Program.js";

export class wccnosy extends Program
{
	website = "http://www.dreamlandbbs.com/filegate/wcf/4utl/index.html";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website : "http://www.dreamlandbbs.com/filegate/wcf/4utl/index.html"
};

exports.dos = () => "WCCNOSY.EXE";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.dosData = (state, p, r) => ({timeout : XU.MINUTE, autoExec : [`WCCNOSY.EXE /indent=2 ${r.args[0]}`, `COPY ${path.basename(r.args[0], path.extname(r.args[0]))}.WC$ OUT`]});
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "IN.WC$"), path.join(state.output.absolute, `${state.input.name}.wc$`))(state, p, cb);
*/
