/*
import {Program} from "../../Program.js";

export class guideml extends Program
{
	website = "http://aminet.net/package/text/hyper/guideml";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "http://aminet.net/package/text/hyper/guideml",
	unsafe  : true
};

exports.qemu = () => "GuideML_OS4";
exports.args = (state, p, r, inPath=state.input.filePath) => (["FILE", inPath, "TO", "HD:out/"]);

// GuideML can just hang forever, or crash, but both cases seem to be handled ok by the supervisor.rexx script and it's internal 180.0 second (3 minutes) timeout
exports.qemuData = (state, p, r) => ({osid : "amigappc", inFilePaths : [r.args[1]]});
*/
