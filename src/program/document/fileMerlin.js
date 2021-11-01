"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path");

exports.meta =
{
	website : "http://www.file-convert.com/flmn.htm",
	flags          :
	{
		// For a list of valid SRC and DEST format names, see programs_formats.txt
		fileMerlinSrcFormat  : "Which format to specify for the input format. Default: AUTO (let FileMerlin decide)",
		fileMerlinDestFormat : "Which format to specify for the output. Default: PDF",
		fileMerlinExt        : "Which extension to use for the output file. Default: .pdf"
	}
};

exports.qemu = () => "c:\\ACI Programs\\FMerlin\\fmn.exe";
exports.args = (state, p, r, inPath=state.input.filePath) => { r.inFilePath = inPath; return [`in(${inPath})`, `sfrm(${r.flags.fileMerlinSrcFormat || "AUTO"})`, "out(c:\\out\\*.pdf)", `dfrm(${r.flags.fileMerlinDestFormat || "PDF"})`]; };
exports.qemuData = (state, p, r) => ({osid : "winxp", timeout : XU.MINUTE, inFilePaths : [r.inFilePath]});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function renameFilesAndRemoveGraphics()
		{
			p.util.file.move(path.join(state.output.absolute, `in${r.flags.fileMerlinExt || ".pdf"}`), path.join(state.output.absolute, `${state.input.name}${r.flags.fileMerlinExt || ".pdf"}`))(state, p, this.parallel());

			// FileMerlin extracts all graphics into a _g subdir. They are not needed, as they are all contained within the PDF
			p.util.file.unlink(path.join(state.output.absolute, `in${r.flags.fileMerlinExt || ".pdf"}_g`))(state, p, this.parallel());
		},
		cb
	);
};
