/*
import {Format} from "../../Format.js";

export class rsrc extends Format
{
	name = "MacOS Resource Fork";
	website = "http://fileformats.archiveteam.org/wiki/Macintosh_resource_file";
	ext = [".rsrc"];
	magic = ["Mac OSX datafork font","AppleDouble Resource Fork","AppleDouble encoded Macintosh file","Mac AppleDouble encoded"];

steps = [null,null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	name    : "MacOS Resource Fork",
	website : "http://fileformats.archiveteam.org/wiki/Macintosh_resource_file",
	ext     : [".rsrc"],
	magic   : ["Mac OSX datafork font", "AppleDouble Resource Fork", "AppleDouble encoded Macintosh file", "Mac AppleDouble encoded"]
};

exports.steps =
[
	() => (state, p, cb) => fs.mkdir(path.join(state.cwd, "rsrc"), {recursive : true}, cb),
	state => ({program : "deark", argsd : [undefined, path.join(state.cwd, "rsrc")], flags : {"dearkOpts" : ["applesd:extractrsrc=1"]}}),
	() => (state, p, cb) =>
	{
		tiptoe(
			function findRSRCFiles()
			{
				fileUtil.glob(path.join(state.cwd, "rsrc"), "**", {nodir : true}, this);
			},
			function convertRSRCFiles(rsrcFilePaths)
			{
				if(rsrcFilePaths.length===0)
				{
					p.util.program.run("deark")(state, p, cb);
					return;
				}

				rsrcFilePaths.serialForEach((rsrcFilePath, subcb) => p.util.program.run("resource_dasm", {flags : {copyOriginalOnFail : true}, argsd : [rsrcFilePath]})(state, p, subcb), this);
			},
			cb
		);
	}
];

*/
