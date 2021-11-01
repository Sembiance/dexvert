"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	website : "https://www.libreoffice.org",
	unsafe  : true,
	flags   :
	{
		sofficeType : `Which format to transform into ("svg", "csv", "pdf", "png", etc). Default is "png" for images or "pdf" for everything else.`
	}
};

exports.qemu = () => "soffice";
exports.args = (state, p, r, inPath=state.input.filePath) => (["--headless", "--convert-to", (r.flags.sofficeType || (state.id.family==="image" ? "png" : "pdf")), "--outdir", "/out", inPath]);
exports.qemuData = (state, p, r) => ({osid : "gentoo", timeout : XU.MINUTE*2, inFilePaths : [r.args.last()]});

exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function findOutputfiles()
		{
			fileUtil.glob(state.output.absolute, "*", {nodir : true}, this);
		},
		function renameFiles(outputFilePaths)
		{
			this.data.outputFilePaths = outputFilePaths;

			outputFilePaths.parallelForEach((outputFilePath, subcb) =>
			{
				const finalOutputFilePath = path.join(path.dirname(outputFilePath), path.basename(outputFilePath).replaceAll(path.basename(r.args.last(), path.extname(r.args.last())), state.input.name));

				// SVG files produced by TotalCADConverter have a border, let's crop it by modifying our viewBox
				if(r.flags.sofficeType==="svg")
					p.util.program.run("deDynamicSVG", {argsd : [outputFilePath, finalOutputFilePath]})(state, p, subcb);
				else
					fileUtil.move(outputFilePath, finalOutputFilePath, subcb);
			}, this);
		},
		function removeOriginals()
		{
			this.data.outputFilePaths.parallelForEach((outputFilePath, subcb) => p.util.file.unlink(outputFilePath)(state, p, subcb), this);
		},
		cb
	);
};
