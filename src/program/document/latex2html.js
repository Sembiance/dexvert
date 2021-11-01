"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website       : "https://www.latex2html.org/",
	gentooPackage : "dev-tex/latex2html"
};

// If you need more .sty files from CTAN, can download them recursively with: ncftpget -R -v "ftp://ftp.math.utah.edu/pub/ctan/tex-archive/macros/latex209/contrib/"
exports.bin = () => "latex2html";
exports.runOptions = () => ({timeout : XU.MINUTE*2, env : {TEXINPUTS : path.join(__dirname, "..", "..", "..", "texmf")}});
exports.args = (state, p, r, inPath=state.input.filePath, outPath=state.output.dirPath) => (["-tmp", state.cwd, "-noinfo", "-html_version", "3.2,unicode,frame,math", "-image_type", "png", "-dir", outPath, inPath]);

// If latex2html craps out, it leaves just a single TMP dir behind. Delete it so that other converters can try converting
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function removeFiles()
		{
			p.util.file.unlink(path.join(state.output.absolute, "images.log"))(state, p, this.parallel());
			p.util.file.unlink(path.join(state.output.absolute, "images.tex"))(state, p, this.parallel());
			p.util.file.unlink(path.join(state.output.absolute, "WARNINGS"))(state, p, this.parallel());
			p.util.file.unlink(path.join(state.output.absolute, "TMP"))(state, p, this.parallel());
		},
		cb
	);
};
