"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe");

exports.meta =
{
	name             : "WebP Image",
	website          : "http://fileformats.archiveteam.org/wiki/Webp",
	ext              : [".webp"],
	mimeType         : "image/webp",
	magic            : ["WebP bitmap", /^WebP$/, /^RIFF.* Web\/P image$/]
};

exports.inputMeta = (state, p, cb) =>
{
	tiptoe(
		function getWebPInfo()
		{
			p.util.program.run(p.program.webpinfo)(state, p, this);
		},
		function stashResults()
		{
			// Check to see if we are an animated WEBP
			if(state.run.webpinfo && state.run.webpinfo.length>0 && state.run.webpinfo[0] && state.run.webpinfo[0].trim().includes("Animation: 1"))
			{
				state.input.meta.webp = {animated : true};
				state.convertExt = ".gif";
			}

			this();
		},
		cb
	);
};

exports.converterPriorty = ["convert"];
