"use strict";
const XU = require("@sembiance/xu");

exports.pre = function pre(state, p)
{
	const formatMeta = p.formats[state.id.family][state.id.formatid].meta;
	return [
		p.util.file.tmpCWDCreate,
		p.util.file.safeInput(formatMeta.safeExt ? formatMeta.safeExt(state) : (formatMeta.ext ? formatMeta.ext[0] : "")),
		p.util.file.safeOutput,
		p.util.meta.input
	];
};

exports.post = function post(state, p)
{
	return [
		p.process.post,
		p.util.file.tmpCWDCleanup
	];
};
