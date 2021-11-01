/*
import {Format} from "../../Format.js";

export class latex extends Format
{
	name = "LaTeX Document";
	website = "http://fileformats.archiveteam.org/wiki/LaTeX";
	ext = [".tex",".ltx"];
	magic = ["LaTeX document","LaTeX 2e document"];
	keepFilename = true;
	filesOptional = undefined;
	notes = "Images don't seem to work at all. Hrm. At least the text seems to make it out, which is good enough for later indexing.";
	converters = ["latex2html","latex2pdf","strings"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name          : "LaTeX Document",
	website       : "http://fileformats.archiveteam.org/wiki/LaTeX",
	ext           : [".tex", ".ltx"],
	magic         : ["LaTeX document", "LaTeX 2e document"],
	keepFilename  : true,
	filesOptional : (state, otherFiles, otherDirs) => ([...otherFiles, ...otherDirs]), // Latex files often reference several other files/directories, so include symlinks to everything else
	notes         : "Images don't seem to work at all. Hrm. At least the text seems to make it out, which is good enough for later indexing."
};

exports.converterPriority = ["latex2html", "latex2pdf", "strings"];

*/
