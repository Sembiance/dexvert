import {Format} from "../../Format.js";

export class latex extends Format
{
	name           = "LaTeX Document";
	website        = "http://fileformats.archiveteam.org/wiki/LaTeX";
	ext            = [".tex", ".ltx"];
	forbidExtMatch = true;
	magic          = ["LaTeX document", "LaTeX 2e document", "BibTeX Generated Bibliography", "LaTeX Font Definition", "LaTeX sorted glossary", "LyX document", /^text\/x-tex$/, "application/x-lyx", /^fmt\/(280|281)( |$)/];
	forbiddenMagic = ["RIS citation format", "Andrew Raster object :atk:"];
	keepFilename   = true;
	auxFiles       = (input, otherFiles, otherDirs) => ((otherFiles.length>0 || otherDirs.length>0) ? [...otherFiles, ...otherDirs] : false);	// Latex files often reference several other files/directories, so include symlinks to everything else
	notes          = "Images don't seem to work at all (abydos.atk). Hrm. At least the text seems to make it out, which is good enough for later indexing.";
	converters     = ["latex2html", "latex2pdf"];
}
