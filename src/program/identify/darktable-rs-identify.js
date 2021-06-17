"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	website       : "https://github.com/Sembiance/dexmagic",
	informational : true
};

exports.bin = () => "darktable-rs-identify";
exports.args = (state, p, r, inPath=state.input.filePath) => ([inPath]);
exports.runOptions = () => ({"ignore-stderr" : true});
exports.post = (state, p, r, cb) =>
{
	const meta = (r.results || "").trim().split("\n").map(line => (line.match(/^(?<k>[^:]+):\s+(?<v>.+)$/) || {groups : {}}).groups).reduce((result, {k, v}) => { result[k] = (v || "").replaceAll("/n", ""); return result; }, {});

	Object.assign(r.meta, meta);

	setImmediate(cb);
};
