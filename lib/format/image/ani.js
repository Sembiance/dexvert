"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	imageUtil = require("@sembiance/xutil").image;

exports.meta =
{
	name             : "Microsoft Windows Animated Cursor",
	website          : "http://fileformats.archiveteam.org/wiki/ANI",
	ext              : [".ani"],
	mimeType         : "application/x-navi-animation",
	magic            : ["Windows Animated Cursor", /^RIFF .* animated cursor$/]
};

exports.steps =
[
	(state, p) => p.util.flow.serial(p.family.converterSteps),
	() => (state, p, cb) =>
	{
		if(!state.output.files || state.output.files.length===0)
			return setImmediate(cb);

		tiptoe(
			function getIconSizeCount()
			{
				// Deark extracts each 'frame' of the animated icon as a seperate ICO file
				// Each ICO file can have multiple sizes within it, so we identify the first output ICO to determine how many sub-sizes it has
				p.util.program.run(p.program.identify, {args : [path.join(state.output.absolute, state.output.files[0])]})(state, p, this);
			},
			function createOutputGIF()
			{
				const iconSizeCount = state.run.identify[0].trim().split("\n").length;

				state.aniOutputGIFPath = path.join(state.output.absolute, `${state.input.name}.gif`);

				const args = ["-delay", "10", ...state.output.files.map(filePath => path.join(state.output.absolute, `${filePath}[${iconSizeCount-1}]`)), state.aniOutputGIFPath];
				p.util.program.run(p.program.convert, {args})(state, p, this);
			},
			function verifyOutputGIF()
			{
				imageUtil.getInfo(state.aniOutputGIFPath, this);
			},
			function cleanupOutputFiles(outputGIFInfo)
			{
				if(!outputGIFInfo || !outputGIFInfo.width || !outputGIFInfo.height)
					return this();
				
				state.output.files.slice().parallelForEach((filePath, subcb) => fileUtil.unlink(path.join(state.output.absolute, filePath), subcb), this);
				state.output.files.length = 0;
				state.output.files.push(path.basename(state.aniOutputGIFPath));

				delete state.aniOutputGIFPath;
			},
			cb
		);
	}
];

exports.converterPriorty = ["deark"];
