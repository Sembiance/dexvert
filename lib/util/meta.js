"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.input = function input(state, p, cb)
{
	tiptoe(
		function getInputFileMeta()
		{
			fs.stat(state.input.absolute, this.parallel());

			const format = p.formats[state.id.family][state.id.formatid];
			if(format.inputMeta)
				format.inputMeta(state, p, this.parallel());
		},
		function storeInputFileMeta(inputFileStat)
		{
			state.input.meta.size = inputFileStat.size;

			this();
		},
		cb
	);
};
