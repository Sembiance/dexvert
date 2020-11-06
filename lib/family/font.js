"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	fs = require("fs"),
	runUtil = require("@sembiance/xutil").run,
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe");

exports.steps =
[
	(state, p) => (p.format.steps ? p.util.flow.serial(p.format.steps) : p.util.flow.noop),
	(state, p) => p.format.post || p.util.flow.noop,
	() => exports.validateOutputFiles
];

exports.validateOutputFiles = function validateOutputFiles(state, p, cb)
{
	(state.output.files || []).slice().parallelForEach((outSubPath, subcb) =>
	{
		const outFilePath = path.join(state.output.absolute, outSubPath);
		tiptoe(
			function getFontInfo()
			{
				runUtil.run("otfinfo", ["-i", outFilePath], runUtil.SILENT, this);
			},
			function removeIfNeeded(fontInfo)
			{
				if(fontInfo && fontInfo.toLowerCase().split("\n").some(line => line.trim.startsWith("family:")))
					return this();
				
				state.output.files.removeOnce(outSubPath);
				if(state.output.files.length===0)
					delete state.output.files;

				fileUtil.unlink(outFilePath, this);
			},
			subcb
		);
	}, cb);
};

const SVG_PREVIEW_FILENAME = "dexvert-font-preview.svg";

// Will create an SVG file that references the input font
exports.previewSteps =
[
	() => (state, p, cb) => fs.writeFile(path.join(state.cwd, SVG_PREVIEW_FILENAME), `<svg xmlns="http://www.w3.org/2000/svg" version="1.1">
    <defs>
        <style>
			@font-face{font-family:&quot;${state.input.meta.font.family.escapeXML()}&quot;;src:url(&quot;${path.join(state.cwd, state.input.filePath).escapeXML()}&quot;)}
        </style>
    </defs>
    <g>
		<text font-size="18pt" font-family="${state.input.meta.font.family.escapeXML()}, Arial">
			<tspan x="0" y="18pt">abcdefghijklmnopqrstuvwxyz</tspan>
			<tspan x="0" dy="26pt">ABCDEFGHIJKLMNOPQRSTUVWXYZ</tspan>
			<tspan x="0" dy="26pt">0123456789\`~!@#$%^&amp;*()-_+=&gt;,&lt;.[]{}|\\:;"'/?</tspan>
			<tspan x="0" dy="26pt"> ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿</tspan>
			<tspan x="0" dy="26pt">ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞß</tspan>
			<tspan x="0" dy="26pt">àáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ</tspan>
		</text>
		<text dy="190pt" font-size="18pt" font-family="${state.input.meta.font.family.escapeXML()}, Arial">
			<tspan x="0" y="0">12</tspan><tspan x="28pt" font-size="12pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="26pt">18</tspan><tspan x="28pt" font-size="18pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="30pt">24</tspan><tspan x="28pt" font-size="24pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="36pt">36</tspan><tspan x="28pt" font-size="36pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="48pt">48</tspan><tspan x="28pt" font-size="48pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="60pt">60</tspan><tspan x="28pt" font-size="60pt">The quick brown fox jumps over the lazy dog.</tspan>
			<tspan x="0" dy="72pt">72</tspan><tspan x="28pt" font-size="72pt">The quick brown fox jumps over the lazy dog.</tspan>
		</text>
    </g>
</svg>`, XU.UTF8, cb),
	state => ({program : "inkscape", args : [`--actions=export-area-drawing; export-filename:${path.join(state.output.dirPath, `${state.input.name}.png`)}; export-do;`, path.join(state.cwd, SVG_PREVIEW_FILENAME)]})
];

// Standard inputMeta function for fonts we support
exports.supportedInputMeta = function supportedInputMeta(state, p, cb)
{
	tiptoe(
		function getImageInfo()
		{
			p.util.program.run("fc-scan")(state, p, this);
		},
		function stashMeta()
		{
			if(p.util.program.getMeta(state, "fc-scan"))
				state.input.meta.font = p.util.program.getMeta(state, "fc-scan");

			this();
		},
		cb
	);
};

exports.updateProcessed = function updateProcessed(state, p, cb)
{
	// Archive extraction is successful if there are any files.
	if(state.output.files)
		state.processed = true;

	if(p.format.updateProcessed)
		return p.format.updateProcessed(state, p, cb);
	
	setImmediate(cb);
};
