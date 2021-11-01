"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	runUtil = require("@sembiance/xutil").run,
	fs = require("fs"),
	path = require("path");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexvert",
	gentooPackage : "app-text/xmlstarlet",
	unsafe        : true
};

exports.args = (state, p, r, inPath=state.input.absolute, outPath=path.join(state.output.absolute, "outfile.svg")) => ([inPath, outPath]);
exports.steps = (s0, p0, r) => [
	() => (state, p, cb) =>
	{
		tiptoe(
			function copyFile()
			{
				if(r.args[0]===r.args[1])
					return this();

				fs.copyFile(r.args[0], r.args[1], this);
			},
			function removeMetaTags()
			{
				// The <title> and <desc> tags often have 'dynamic' info like current date and time of file generation, let's delete this uselessness so tests run better and labeling can know it's seen the file before
				runUtil.run("xmlstarlet", ["ed", "--inplace", "-N", "s=http://www.w3.org/2000/svg", "--delete", "/s:svg/s:*[local-name()='desc' or local-name()='title' or local-name()='metadata']", r.args[1]], {silent : !state.verbose}, this);
			},
			function removeMetaAttributes()
			{
				// A top level 'id' attribute on <svg> serves no real purpose other than to change the hash of the file every time it's generate, so let's get rid of it
				runUtil.run("xmlstarlet", ["ed", "--inplace", "-N", "s=http://www.w3.org/2000/svg", "--delete", "/s:svg/@id", r.args[1]], {silent : !state.verbose}, this);
			},
			function optimizeSVG()
			{
				// This will take care of deleting any 'empty' elements that totalCADConverter often does
				p.util.program.run("svgo", {argsd : [r.args[1]]})(state, p, this);
			},
			cb
		);
	}
];
