/*
import {Program} from "../../Program.js";

export class IsoBuster extends Program
{
	website = "https://www.isobuster.com/isobuster.php";
	unsafe = true;
	slow = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website : "https://www.isobuster.com/isobuster.php",
	unsafe  : true,	// Takes too long,
	slow    : true
};

exports.qemu = () => "c:\\Program Files\\Smart Projects\\IsoBuster\\IsoBuster.exe";

// IsoBuster command line options: https://www.isobuster.com/help/use_of_command_line_parameters
exports.args = (state, p, r, inPath=state.input.filePath) => (["/ef:all:C:\\out", inPath, "/c", "/ep:ren", "/ep:rei", "/ep:oeo"]);

// IsoBuster can take a LONG time to run, but 20 minutes should be plenty for any file
exports.qemuData = (state, p, r) => ({osid : "winxp", timeout : XU.MINUTE*20, inFilePaths : [r.args[1], ...(state.extraFilenames || [])]});
*/
