/*
import {Program} from "../../Program.js";

export class ezdxf extends Program
{
	website = "https://ezdxf.mozman.at/";
	gentooPackage = "dev-python/ezdxf";
	gentooOverlay = "dexvert";
	unsafe = true;
}
*/

/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path");

exports.meta =
{
	website       : "https://ezdxf.mozman.at/",
	gentooPackage : "dev-python/ezdxf",
	gentooOverlay : "dexvert",
	unsafe        : true
};

exports.bin = () => "ezdxf";
exports.args = (state, p, r, inPath=state.input.filePath, outPath=path.join(state.output.dirPath, "outfile.svg")) => (["draw", "-o", outPath, inPath]);
exports.post = (state, p, r, cb) => p.util.file.move(path.join(state.output.absolute, "outfile.svg"), path.join(state.output.absolute, `${state.input.name}.svg`))(state, p, cb);
*/
