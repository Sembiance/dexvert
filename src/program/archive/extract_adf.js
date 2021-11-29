/*
import {Program} from "../../Program.js";

export class extract_adf extends Program
{
	website = "https://github.com/mist64/extract-adf";
	gentooPackage = "app-arch/extract-adf";
	gentooOverlay = "dexvert";
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website        : "https://github.com/mist64/extract-adf",
	gentooPackage  : "app-arch/extract-adf",
	gentooOverlay  : "dexvert"
};

exports.bin = () => "extract-adf";

// We extract into a temporary directory in CWD and then move the files after we are done
// This is because extract-adf can produce VERY messed up files that not even standard linux utilities like 'find' can do anything with
// So this prevents issues with really horribly output files gunking everything up
exports.preArgs = (state, p, r, cb) =>	// ROB DENO: preArgs stuff can now just be done inside of args itself, since it's async now
{
	r.extractADFWipPath = fileUtil.generateTempFilePath(state.cwd, "-extract-adf");
	fs.mkdir(r.extractADFWipPath, {recursive : true}, cb);
};

exports.args = (state, p, r, inPath=state.input.filePath) => (["-a", path.relative(r.extractADFWipPath, path.join(state.cwd, inPath))]);
exports.runOptions = (state, p, r) => ({cwd : r.extractADFWipPath});

exports.post = (state, p, r, cb) => p.util.file.moveAllFiles(r.extractADFWipPath, state.output.absolute)(state, p, cb);
*/
