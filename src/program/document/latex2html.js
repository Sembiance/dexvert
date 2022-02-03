import {xu} from "xu";
import {Program} from "../../Program.js";
import {path} from "std";

export class latex2html extends Program
{
	website = "https://www.latex2html.org/";
	package = "dev-tex/latex2html";
	unsafe  = true;

	// If you need more .sty files from CTAN, can download them recursively with: ncftpget -R -v "ftp://ftp.math.utah.edu/pub/ctan/tex-archive/macros/latex209/contrib/"
	bin = "latex2html";

	runOptions = ({
		// Some files hang forever, like document/latex/LATEX.BUG
		timeout : xu.MINUTE,

		// Some files cause an infinite amount of stdout garbage, crashing deno (see text/txt/tabelle.txt)
		stdoutNull : true,
		stderrNull : true,

		// This program likes to leave around a '^.*$' process running roever, so we need to kill it's childrens
		killChildren : true,

		// Specify where our texmf files live
		env : {TEXINPUTS : path.join(xu.dirname(import.meta), "..", "..", "..", "texmf")}
	});
	args = r => ["-tmp", r.f.root, "-noinfo", "-html_version", "3.2,unicode,frame,math", "-image_type", "png", "-dir", r.outDir(), r.inFile()];

	// If latex2html craps out, it leaves just a single TMP dir behind. Delete it so that other converters can try converting. Also delete some other junk files it may leave
	verify    = (r, dexFile) => !((dexFile.dir===r.outDir({absolute : true}) && ["images.log", "images.tex", "images.pdf", "WARNINGS"].includes(dexFile.base)) || dexFile.rel.startsWith(`${r.outDir()}/TMP`));
	renameOut = false;
}
